"""Prometheus class for Alert Exporter."""
import json

from kubernetes import client, config


class Prometheus:
    """
    A wrapper for the Prometheus boto client
    """

    def __init__(self) -> None:
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def get_rules(self) -> None:
        self.rules = {}
        rules = self.client.describe_alarms()
        print(json.dumps(rules, indent=2))
