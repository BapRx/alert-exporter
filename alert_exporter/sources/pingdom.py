"""Pingdom class for Alert Exporter."""

import logging
import time
from datetime import timedelta

import requests
from humanize import naturaldelta


class Pingdom:
    """
    A wrapper for the Pingdom API
    """

    def __init__(self, api_key: str, debug: bool) -> None:
        self.api_key = api_key
        self.base_url = "https://api.pingdom.com/api/3.1"
        self.debug = debug
        self.checks = []

    def get_detailed_check(self, check_id) -> None:
        logging.debug(f"Collecting detailed information about Pingdom check {check_id}")
        response = requests.get(
            f"{self.base_url}/checks/{check_id}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        if response.status_code == 429:
            time.sleep(5)
            self.get_detailed_check(check_id)
        elif response.status_code >= 400 and self.debug:
            logging.warning(f"Error while fetching Pingdom check {check_id}:")
            print(f"HTTP status code: {response.status_code}")
            print(f"HTTP raw response:\n{response.text}")
            print(f"HTTP JSON response:\n{response.json()}")
        check = response.json()["check"]
        check["tags"] = [t["name"] for t in check["tags"]]
        check["paused"] = True if check["status"] == "paused" else False
        if "http" in check["type"]:
            scheme = "https://" if check["type"]["http"]["port"] == 443 else "http://"
            check["url"] = scheme + check["hostname"] + check["type"]["http"]["url"]
        check["responsetime_threshold"] = naturaldelta(
            timedelta(milliseconds=check["responsetime_threshold"])
        )
        self.checks.append(check)

    def get_checks(self, tags: str) -> None:
        logging.info("Fetching Pingdom checks")
        response = requests.get(
            f"{self.base_url}/checks",
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
            self.get_detailed_check(check["id"])
