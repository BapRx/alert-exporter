"""Console script for alert_exporter."""
import argparse
import logging
import os
import sys

from alert_exporter.sources.cloudwatch import Cloudwatch
from alert_exporter.sources.kubernetes import Kubernetes


def main():
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--prometheus", default=False, action="store_true")
    parser.add_argument("--context", default=None)
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    parser.add_argument("--aws-profile", default=os.getenv("AWS_PROFILE", None))
    parser.add_argument(
        "--aws-region",
        help="Specific region to target. Default: Iterate over all regions available.",
    )
    args = parser.parse_args()

    rules = []
    if args.prometheus:
        k = Kubernetes(context=args.context)
        k.get_prometheus_rules()
        rules += k.rules
    if args.cloudwatch:
        c = Cloudwatch(profile=args.aws_profile, region=args.aws_region)
        c.get_alarms()
        rules += c.rules
    if len(rules) == 0:
        logging.warning("No alert rule found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
