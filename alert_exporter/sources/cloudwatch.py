"""Cloudwatch class for Alert Exporter."""

import logging
from datetime import timedelta
from time import sleep

import boto3
from botocore.exceptions import ClientError
from humanize import naturaldelta

COMPARISON_OPERATORS = {
    "GreaterThanOrEqualToThreshold": ">=",
    "GreaterThanThreshold": ">",
    "LessThanOrEqualToThreshold": "<=",
    "LessThanThreshold": "<",
}


class Cloudwatch:
    """
    A wrapper for the Cloudwatch boto client
    """

    def __init__(self, profile: str, region: str) -> None:
        self.session = boto3.session.Session(profile_name=profile)
        if region:
            self.regions = [region]
        else:
            self.regions = self.session.get_available_regions(service_name="cloudwatch")

    def init_client(self, region: str) -> None:
        self.client = self.session.client("cloudwatch", region_name=region)

    def get_alarms(self) -> None:
        self.rules = []
        for region in self.regions:
            self.init_client(region)
            try:
                alarms = self.client.describe_alarms()
            except ClientError as e:
                logging.debug(f"Error while describing alarms in region {region}: ", e)
                continue
            for alarm_type in ["CompositeAlarms", "MetricAlarms"]:
                self.rules += [
                    {
                        "region": region,
                        "type": alarm_type,
                        "name": r.get("AlarmName", ""),
                        "description": r.get("AlarmDescription", ""),
                        "rule": (
                            f'{r.get("MetricName")}'
                            f' {COMPARISON_OPERATORS[r.get("ComparisonOperator")]}'
                            f' {r.get("Threshold")}'
                            f' for {r.get("EvaluationPeriods")} datapoints within'
                            f' {naturaldelta(timedelta(seconds=r.get("Period")))}'
                        ),
                    }
                    for r in alarms[alarm_type]
                ]
            sleep(0.5)
