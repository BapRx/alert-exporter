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
Extract alerts configured in different sources (eg: Prometheus Rules, CloudWatch Alarms, Pingdom)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR}
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
  --jinja-template [JINJA_TEMPLATE]
  -f {markdown,yaml,html}, --format {markdown,yaml,html}
  --prometheus
  --prometheus-filters PROMETHEUS_FILTERS
  --context [CONTEXT]
  --cloudwatch
  --aws-profile AWS_PROFILE
  --aws-region AWS_REGION
                        Specific region to target. Default: Iterate over all regions available.
  --pingdom
  --pingdom-api-key PINGDOM_API_KEY
  --pingdom-tags PINGDOM_TAGS
                        Comma separated list of tags. Eg: tag1,tag2
```

### Multiple sources are available, one or many can be selected

#### Kubernetes / Prometheus

The current context is used unless you provide the `--context` flag.

```bash
alert-exporter -o minikube.html --prometheus --context minikube
```

You can filter prometheus rule to match specific labels using the '--prometheus-filters' flag.

```bash
alert-exporter -o minikube.html --prometheus --context minikube --prometheus-filters '{"severity": "critical"}'
```

#### AWS Cloudwatch

All available regions are parsed unless you provide the `--aws-region` flag.

You need to be authenticated before using this tool.

```bash
alert-exporter -o aws.html --cloudwatch --aws-region eu-west-1 --aws-profile profile
```

#### Pingdom

An API key with read only permission is required to fetch the checks. The key can be provided in the `PINGDOM_API_KEY` environment variable.

```bash
alert-exporter -o pingdom.html --pingdom --pingdom-tags example-tag
```

#### Multiple sources at once

```bash
alert-exporter -o combined.html --prometheus --cloudwatch --aws-region eu-west-1
```

### Formats

Predefined formats are provided with this tool:

- HTML
- Markdown
- YAML

You can use a custom format by providing a Jinja2 file with the `--jinja-template` flag.

## HTML output example

<a href="https://raw.githubusercontent.com/BapRx/alert-exporter/master/docs/alerts-html.png"><img alt="HTML output" src="https://raw.githubusercontent.com/BapRx/alert-exporter/master/docs/alerts-html.png"></a>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
