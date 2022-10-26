"""Pingdom class for Alert Exporter."""

import logging

import requests


class Pingdom:
    """
    A wrapper for the Pingdom API
    """

    def __init__(self, api_key: str, debug: bool) -> None:
        self.api_key = api_key
        self.debug = debug

    def get_checks(self, tags: str) -> None:
        logging.info("Fetching Pingdom checks")
        response = requests.get(
            "https://api.pingdom.com/api/3.1/checks",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            params={"include_tags": True, "tags": tags},
        )
        if response.status_code >= 400 and self.debug:
            logging.warning("Error while fetching Pingdom checks:")
            print(f"HTTP status code: {response.status_code}")
            print(f"HTTP raw response:\n{response.text}")
            print(f"HTTP JSON response:\n{response.json()}")
        checks = response.json()["checks"]
        for check in checks:
            check["tags"] = [t["name"] for t in check["tags"]]
        self.checks = checks
