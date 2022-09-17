"""Kubernetes class for Alert Exporter."""
import json
import logging
import sys

from kubernetes import client, config


class Kubernetes:
    """
    A wrapper for the Kubernetes client
    """

    def __init__(self, context: str) -> None:
        config.load_kube_config()
        contexts, active_context = config.list_kube_config_contexts()
        available_contexts = [c["name"] for c in contexts]
        if context and context not in available_contexts:
            logging.error(
                f"Context {context} not found in {config.KUBE_CONFIG_DEFAULT_LOCATION}"
            )
            logging.info("Available contexts:")
            print("\n".join(available_contexts))
            sys.exit(1)

        if context:
            logging.info(f"Using context {context}")
            config.load_kube_config(context=context)
        else:
            logging.info(f"Using context {active_context.get('name')}")
        self.client = client.CoreV1Api()

    def get_prometheus_rules(self) -> None:
        self.rules = []
        crd_api = client.CustomObjectsApi()
        rules = crd_api.list_cluster_custom_object(
            group="monitoring.coreos.com", version="v1", plural="prometheusrules"
        )
        for pr in rules.get("items", []):
            prometheus_rule_name = pr["metadata"]["name"]
            logging.info(f"Prometheus Rule - {prometheus_rule_name}")
            for grp in pr["spec"]["groups"]:
                self.rules += [
                    {
                        "PrometheusRule": prometheus_rule_name,
                        "group": grp.get("name"),
                        "expr": r.get("expr"),
                    }
                    for r in grp["rules"]
                ]
        print(json.dumps(self.rules, indent=2))
