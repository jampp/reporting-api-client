#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cookiecutter-python version: 0.4.1
"""The setup script."""
import os

from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(os.path.join(setup_dir, filename)) as requirements_file:
        requirements = requirements_file.readlines()
        # Remove all lines that are comments
        requirements = [
            line for line in requirements if not line.strip().startswith("#")
        ]
        # Remove pip flags
        requirements = [
            line for line in requirements if not line.strip().startswith("--")
        ]
        # Remove inline comments
        requirements = [
            line.split("#", 1)[0] if "#" in line else line for line in requirements
        ]
        # Remove empty lines
        requirements = list(filter(None, requirements))
        # Remove whitespaces
        requirements = [line.strip().replace(" ", "") for line in requirements]
        return requirements


cmd_class = {}
setup_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(setup_dir, "README.rst"), encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open(os.path.join(setup_dir, "CHANGELOG.rst"), encoding="utf-8") as history_file:
    history = history_file.read()

with open(
    os.path.join(setup_dir, "reporting_api_client", "VERSION"),
    "r",
    encoding="utf-8",
) as vf:
    version = vf.read().strip()


setup(
    name="jampp_reporting_api_client",
    description="Client for Reporting API.",
    version=version,
    author="Jampp",
    author_email="data-infra@jampp.com",
    install_requires=[parse_requirements("requirements.in")],
    extras_require={
        "dev": parse_requirements("requirements-dev.txt"),
        "pandas": ["pandas"],
    },
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    package_data={
        "": ["*.pxd", "*.pyx"],
        "reporting_api_client": ["VERSION"],
    },
    packages=find_packages(include=["reporting_api_client", "reporting_api_client.*"]),
    test_suite="tests",
    tests_require=[
        "pytest==4.6.3",
    ],
    url="https://github.com/jampp/reporting-api-client",
    zip_safe=False,
)
