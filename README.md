# Alert Exporter

<p>
<a href="https://pypi.org/project/alert-exporter/"><img alt="PyPI" src="https://img.shields.io/pypi/v/alert-exporter"></a>
<a href="https://pypi.org/project/alert-exporter/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/alert-exporter"></a>
<a href="https://github.com/BapRx/alert-exporter/"><img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/BapRx/alert-exporter"></a>
<a href="https://pypi.org/project/alert-exporter/"><img alt="PyPI - Status" src="https://img.shields.io/pypi/status/alert-exporter"></a>
</p>

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install alert-exporter.

```bash
pip install alert-exporter
```

## Usage

```bash
❯ alert-exporter --help
Extract alerts configured in different sources (eg: Prometheus Rules, CloudWatch Alarms, etc.)

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR}
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
  --jinja-template [JINJA_TEMPLATE]
  -f {markdown,csv,html,yaml}, --format {markdown,csv,html,yaml}
  --prometheus
  --context [CONTEXT]
  --cloudwatch
  --aws-profile AWS_PROFILE
  --aws-region AWS_REGION
                        Specific region to target. Default: Iterate over all regions available.
```

### Multiple sources are available, one or many can be selected

#### Kubernetes / Prometheus

The current context is used unless you provide the `--context` flag.

```bash
alert-exporter -o minikube.html --prometheus --context minikube
```

#### AWS Cloudwatch

All available regions are parsed unless you provide the `--aws-region` flag.

You need to be authenticated before using this tool.

```bash
alert-exporter -o aws.html --cloudwatch --aws-region eu-west-1 --aws-profile profile
```

#### Multiple sources at once

```bash
alert-exporter -o combined.html --prometheus --cloudwatch --aws-region eu-west-1
```

### Formats

Predefined formats are provided with this tool:

- HTML
- Markdown
- CSV
- YAML

You can use a custom format by providing a Jinja2 file with the `--jinja-template` flag.

## HTML output example

<a href="https://raw.githubusercontent.com/BapRx/alert-exporter/master/docs/alerts-html.png"><img alt="HTML output" src="https://raw.githubusercontent.com/BapRx/alert-exporter/master/docs/alerts-html.png"></a>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
