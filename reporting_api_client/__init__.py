# -*- coding: utf-8 -*-
import os.path

from reporting_api_client.client import ReportingAPIClient


with open(os.path.join(os.path.dirname(__file__), "VERSION"), "r") as vf:
    __version__ = vf.read().strip()


__all__ = [
    "ReportingAPIClient",
    "__version__",
]
