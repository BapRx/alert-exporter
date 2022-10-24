"""Kubernetes class for Alert Exporter."""
import logging
import sys

from kubernetes import client, config


class Kubernetes:
    """
    A wrapper for the Kubernetes client
    """

    def __init__(self, context: str, filters: dict) -> None:
        self.rules = []
        self.filters = filters
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
                        "promRuleName": prometheus_rule_name,
                        "name": "/".join(
                            filter(None, [r.get("alert"), grp.get("name")])
                        ),
                        "description": r.get("annotations", {}).get("description", ""),
                        "summary": r.get("annotations", {}).get("summary", ""),
                        "expr": r.get("expr", ""),
                        "for": r.get("for", ""),
                        "severity": r.get("labels", {}).get("severity", ""),
                        "runbook": r.get("annotations", {}).get("runbook_url", ""),
                    }
                    for r in grp["rules"]
                    if all(
                        r.get("labels", {}).get(k) == v for k, v in self.filters.items()
                    )
                ]
