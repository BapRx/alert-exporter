"""Console script for alert_exporter."""
import json
import logging
import os
import sys
from argparse import SUPPRESS, ArgumentParser, Namespace
from importlib.metadata import version
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    Template,
    select_autoescape,
)

from alert_exporter.sources.cloudwatch import Cloudwatch
from alert_exporter.sources.kubernetes import Kubernetes
from alert_exporter.sources.pingdom import Pingdom

AVAILABLE_FORMATS = {
    "html": "html",
    "md": "markdown",
    "yaml": "yaml",
    "yml": "yaml",
}


def init_args() -> Namespace:
    parser = ArgumentParser(
        description="Extract alerts configured in different sources"
        " (eg: Prometheus Rules, CloudWatch Alarms, Pingdom)",
        usage=SUPPRESS,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=version("alert-exporter")
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
        ],
    )
    parser.add_argument("-o", "--output-file", required=True)
    parser.add_argument("--jinja-template", nargs="?")
    parser.add_argument("-f", "--format", choices=list(set(AVAILABLE_FORMATS.values())))
    parser.add_argument("--prometheus", default=False, action="store_true")
    parser.add_argument("--prometheus-filters", default={}, type=json.loads)
    parser.add_argument("--context", nargs="?")
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    parser.add_argument("--aws-profile", default=os.getenv("AWS_PROFILE", None))
    parser.add_argument(
        "--aws-region",
        help="Specific region to target. Default: Iterate over all regions available.",
    )
    parser.add_argument("--pingdom", default=False, action="store_true")
    parser.add_argument("--pingdom-api-key", default=os.getenv("PINGDOM_API_KEY", None))
    parser.add_argument(
        "--pingdom-tags",
        default=None,
        help="Comma separated list of tags. Eg: tag1,tag2",
    )
    args = parser.parse_args()

    return args


def validate_args(args: Namespace) -> None:
    if args.pingdom and not args.pingdom_api_key:
        logging.error("A valid Pingdom API key is required to extract checks.")
    else:
        return
    sys.exit(1)


def get_template_file(
    output_file: str, output_format: str, jinja2_template: str
) -> str:
    if output_format:
        if output_format == "markdown":
            return "alerts.md.jinja"
        else:
            return f"alerts.{output_format}.jinja"
    else:
        if jinja2_template:
            return jinja2_template
    file_extension = output_file.split(".")[-1]
    if not file_extension:
        logging.error(
            "The output format couldn't be automatically guessed from the"
            " file extension. Please use one of the available formats"
            " or provide a Jinja2 template."
        )
        sys.exit(1)
    if file_extension in AVAILABLE_FORMATS:
        if AVAILABLE_FORMATS[file_extension] == "markdown":
            return "alerts.md.jinja"
        return f"alerts.{AVAILABLE_FORMATS[file_extension]}.jinja"
    logging.error(
        f"No output format detected for the output file extension '{file_extension}'."
        " If you want to export in a custom format,"
        " you need to provide a Jinja2 file with the --jinja-template flag."
    )
    sys.exit(1)


def render_template(template: Template, alerts: list, output_file: str) -> None:
    rendered = template.render(alerts=alerts)
    if "/" in output_file:
        absolute_file = output_file
    else:
        absolute_file = f"{os.getcwd()}/{output_file}"
    with open(absolute_file, "w+") as f:
        f.write(rendered)


def main():
    args = init_args()
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    validate_args(args)

    alert_count = 0
    if args.cloudwatch:
        c = Cloudwatch(
            profile=args.aws_profile,
            region=args.aws_region,
            debug=bool(args.log_level == "DEBUG"),
        )
        c.get_alarms()
        alert_count += len(c.alarms)
    if args.pingdom:
        p = Pingdom(
            api_key=args.pingdom_api_key,
            debug=bool(args.log_level == "DEBUG"),
        )
        p.get_checks(tags=args.pingdom_tags)
        alert_count += len(p.checks)
    if args.prometheus:
        k = Kubernetes(context=args.context, filters=args.prometheus_filters)
        k.get_prometheus_rules()
        alert_count += len(k.rules)
    if alert_count == 0:
        logging.warning("No alert found.")
        return 1

    if args.jinja_template:
        path = Path(args.jinja_template)
        if not path.exists():
            logging.error(f"The template file {str(path)} does not exist.")
            return 1
        template_file = path.name
        env = Environment(loader=FileSystemLoader(path.parent.absolute()))
    else:
        template_file = get_template_file(
            output_file=args.output_file,
            output_format=args.format,
            jinja2_template=args.jinja_template,
        )
        env = Environment(
            loader=PackageLoader("alert_exporter"), autoescape=select_autoescape()
        )
    template = env.get_template(template_file)
    render_template(
        template=template,
        alerts={
            "cloudwatch": c.alarms if args.cloudwatch else [],
            "pingdom": p.checks if args.pingdom else [],
            "prometheus": k.rules if args.prometheus else [],
        },
        output_file=args.output_file,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
