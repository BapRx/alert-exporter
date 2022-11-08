# Changelog

## 0.1.0 (2022-09-19)

- Initial release on PyPI

## 0.1.1 (2022-09-19)

- Fix broken install due to wrong usage of setup.py
- Rename command line from alert_exporter to alert-exporter

## 0.2.0 (2022-09-20)

- Fix custom template handling when using packaged module
- Update docs
- Release beta version

## 0.2.1 (2022-09-20)

- Fix broken install resulting in ModuleNotFoundError

## 0.2.2 (2022-09-20)

- Implement GreaterThanUpperThreshold and LessThanLowerThreshold alarm thresholds
- Fix error while querying multiple regions
- Increase AWS log level to ERROR unless debug is enabled

## 0.2.3 (2022-09-20)

- Add version command-line flag
- Improve HTML layout for Cloudwatch alerts by moving description in last position

## 0.3.0 (2022-10-24)

- Add --prometheus-filters flag

## 0.3.1 (2022-10-24)

- Fix typo & bump version returned by `alert-exporter --version`

## 0.4.0 (2022-11-08)

- Add Pingdom source to export configured checks
- Remove messy CSV output format
