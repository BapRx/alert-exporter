"""Console script for alert_exporter."""
import logging
import os
import sys
from argparse import SUPPRESS, ArgumentParser, Namespace
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

AVAILABLE_FORMATS = {
    "csv": "csv",
    "html": "html",
    "md": "markdown",
    "yaml": "yaml",
    "yml": "yaml",
}


def init_args() -> Namespace:
    parser = ArgumentParser(
        description="Extract alerts configured in different sources"
        " (eg: Prometheus Rules, CloudWatch Alarms, etc.)",
        usage=SUPPRESS,
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
    parser.add_argument("--context", nargs="?")
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    parser.add_argument("--aws-profile", default=os.getenv("AWS_PROFILE", None))
    parser.add_argument(
        "--aws-region",
        help="Specific region to target. Default: Iterate over all regions available.",
    )
    args = parser.parse_args()

    return args


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


def render_template(template: Template, rules: list, output_file: str) -> None:
    rendered = template.render(rules=rules)
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

    rules = []
    if args.prometheus:
        k = Kubernetes(context=args.context)
        k.get_prometheus_rules()
        rules += k.rules
    if args.cloudwatch:
        c = Cloudwatch(
            profile=args.aws_profile,
            region=args.aws_region,
            debug=bool(args.log_level == "DEBUG"),
        )
        c.get_alarms(profile=args.aws_profile, debug=bool(args.log_level == "DEBUG"))
        rules += c.rules
    if len(rules) == 0:
        logging.warning("No alert rule found.")
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
        rules={
            "prometheus": k.rules if args.prometheus else [],
            "cloudwatch": c.rules if args.cloudwatch else [],
        },
        output_file=args.output_file,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
