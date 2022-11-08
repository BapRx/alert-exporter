"""Cloudwatch class for Alert Exporter."""

import logging
from datetime import timedelta
from time import sleep

import boto3
import botocore
from humanize import naturaldelta

COMPARISON_OPERATORS = {
    "GreaterThanOrEqualToThreshold": ">=",
    "GreaterThanUpperThreshold": ">",
    "LessThanLowerThreshold": "<",
    "GreaterThanThreshold": ">",
    "LessThanOrEqualToThreshold": "<=",
    "LessThanThreshold": "<",
}


class Cloudwatch:
    """
    A wrapper for the Cloudwatch boto client
    """

    def __init__(self, profile: str, region: str, debug: bool) -> None:
        self.debug = debug
        self.profile = profile
        if not self.debug:
            logging.getLogger("boto3").setLevel(logging.ERROR)
            logging.getLogger("botocore").setLevel(logging.ERROR)
        try:
            self.session = boto3.session.Session(profile_name=self.profile)
        except botocore.exceptions.ClientError as e:
            logging.warning(f"Error creating a session with region {region}:")
            if self.debug:
                print(e)
        if region:
            self.regions = [region]
        else:
            self.regions = self.session.get_available_regions(service_name="sts")

    def init_client(self, region: str) -> None:
        self.session = boto3.session.Session(profile_name=self.profile)
        self.client = self.session.client("cloudwatch", region_name=region)

    def build_rule_expression(self, rule: dict) -> str:
        if rule.get("ComparisonOperator") in [
            "GreaterThanUpperThreshold",
            "LessThanLowerThreshold",
        ]:
            metrics = {m["Id"]: m for m in rule["Metrics"]}
            c2 = metrics.pop(rule["ThresholdMetricId"])
            c1 = metrics.pop(next(iter(metrics)))
            if metrics:
                print("DEBUG: Hmmmm weird I didn't expect anything left here.")
            metric_name = c1["MetricStat"]["Metric"]["MetricName"]
            threshold = c2["Expression"]
            period = c1["MetricStat"]["Period"]
        else:
            metric_name = rule.get("MetricName")
            threshold = rule.get("Threshold")
            period = rule.get("Period")
        expression = (
            f"{metric_name}"
            f' {COMPARISON_OPERATORS[rule.get("ComparisonOperator")]}'
            f" {threshold}"
            f' for {rule.get("EvaluationPeriods")} datapoints within'
            f" {naturaldelta(timedelta(seconds=period))}"
        )
        return expression

    def get_alarms(self) -> None:
        self.alarms = []
        for region in self.regions:
            logging.info(f"Getting alarms from region {region}")
            try:
                self.init_client(region=region)
                alarms = self.client.describe_alarms()
            except botocore.exceptions.ClientError as e:
                logging.warning(f"Error while describing alarms in region {region}:")
                if self.debug:
                    print(e)
                continue
            for alarm_type in ["CompositeAlarms", "MetricAlarms"]:
                self.alarms += [
                    {
                        "region": region,
                        "type": alarm_type,
                        "name": r.get("AlarmName", ""),
                        "description": r.get("AlarmDescription", ""),
                        "rule": self.build_rule_expression(rule=r),
                    }
                    for r in alarms[alarm_type]
                ]
            sleep(0.5)
