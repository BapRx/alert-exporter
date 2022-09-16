"""Cloudwatch class for Alert Exporter."""

import json
import os

import boto3


class Cloudwatch:
    """
    A wrapper for the Cloudwatch boto client
    """

    def __init__(self, region: str, profile: str) -> None:
        self.session = boto3.session.Session(
            profile_name=profile or os.getenv("AWS_PROFILE", None)
        )
        self.client = self.session.client("cloudwatch", region_name=region)

    def get_rules(self):
        rules = self.client.describe_alarms()
        print(json.dumps(rules, indent=2, sort_keys=True, default=str))
