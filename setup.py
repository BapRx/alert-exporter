#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["kubernetes", "boto3", "humanize"]

test_requirements = []

setup(
    author="Baptiste ROUX",
    author_email="baptiste.roux@skale-5.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description=(
        "Extract alerts configured in different sources"
        " (eg: Prometheus Rules, CloudWatch Alarms, etc.)"
    ),
    entry_points={
        "console_scripts": [
            "alert_exporter=alert_exporter.cli:main",
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="alert_exporter",
    name="alert_exporter",
    packages=find_packages(include=["alert_exporter", "alert_exporter.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/BapRx/alert_exporter",
    version="0.1.0",
    zip_safe=False,
)
