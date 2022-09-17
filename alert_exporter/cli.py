"""Console script for alert_exporter."""
import argparse
import logging
import os
import sys

from alert_exporter.sources.cloudwatch import Cloudwatch
from alert_exporter.sources.prometheus import Prometheus


def main():
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--prometheus", default=False, action="store_true")
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    parser.add_argument("--aws-profile", default=os.getenv("AWS_PROFILE", None))
    parser.add_argument(
        "--aws-region",
        "Specific region to target. Default: Iterate over all regions available.",
    )
    args = parser.parse_args()

    total_rules = 0
    if args.prometheus:
        p = Prometheus()
        p.get_rules()
        total_rules += len(p.rules)
    if args.cloudwatch:
        c = Cloudwatch(profile=args.aws_profile, region=args.aws_region)
        c.get_rules()
        total_rules += len(c.rules)
    if total_rules == 0:
        logging.warning("No alert rule found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
