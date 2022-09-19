"""Console script for alert_exporter."""
import argparse
import logging
import os
import sys

from jinja2 import Environment, PackageLoader, select_autoescape

from alert_exporter.sources.cloudwatch import Cloudwatch
from alert_exporter.sources.kubernetes import Kubernetes

AVAILABLE_FORMATS = {
    "csv": "csv",
    "html": "html",
    "md": "markdown",
    "yaml": "yaml",
    "yml": "yaml",
}


def init_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        "-f", "--format", choices=list(set(AVAILABLE_FORMATS.values())) + ["custom"]
    )
    parser.add_argument("--prometheus", default=False, action="store_true")
    parser.add_argument("--context", nargs="?")
    parser.add_argument("--cloudwatch", default=False, action="store_true")
    parser.add_argument("--aws-profile", default=os.getenv("AWS_PROFILE", None))
    parser.add_argument(
        "--aws-region",
        help="Specific region to target. Default: Iterate over all regions available.",
    )
    args = parser.parse_args()

    if args.format == "custom" and not args.jinja_template:
        logging.error(
            "You chose to export the result in a custom format."
            " You need to provide a Jinja2 file with the --jinja-template flag."
        )
        sys.exit(1)

    return args


def get_template_file(
    output_file: str, output_format: str, jinja2_template: str
) -> str:
    if output_format:
        if output_format == "custom":
            return jinja2_template
        elif output_format == "markdown":
            return "alerts.md.jinja"
        else:
            return f"alerts.{output_format}.jinja"
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
        f"No template found for the output file extension '{file_extension}'."
    )
    sys.exit(1)


def render_template(template_file: str, rules: list, output_file: str) -> None:
    env = Environment(
        loader=PackageLoader("alert_exporter"), autoescape=select_autoescape()
    )
    template = env.get_template(template_file)
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
        c = Cloudwatch(profile=args.aws_profile, region=args.aws_region)
        c.get_alarms()
        rules += c.rules
    if len(rules) == 0:
        logging.warning("No alert rule found.")
    render_template(
        get_template_file(
            output_file=args.output_file,
            output_format=args.format,
            jinja2_template=args.jinja_template,
        ),
        rules={
            "prometheus": k.rules if args.prometheus else [],
            "cloudwatch": c.rules if args.cloudwatch else [],
        },
        output_file=args.output_file,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
