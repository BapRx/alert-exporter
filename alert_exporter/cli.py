"""Console script for alert_exporter."""
import argparse
import logging
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
    parser.add_argument("--aws-region", default=None)
    parser.add_argument("--aws-profile", default=None)
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    args = parser.parse_args()
    if args.cloudwatch and not args.aws_region:
        logging.error(
            "The option '--cloudwatch' needs the '--aws-region' flag to be provided."
            " (Accepted ENV variables: 'AWS_REGION', 'AWS_DEFAULT_REGION')",
        )
        sys.exit(1)

    rules = {}
    if args.prometheus:
        p = Prometheus()
        rules["prometheus"] = p.get_rules()
    if args.cloudwatch:
        c = Cloudwatch(region=args.aws_region, profile=args.aws_profile)
        rules["cloudwatch"] = c.get_rules()
    if not rules:
        logging.warning("No alert rule found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
