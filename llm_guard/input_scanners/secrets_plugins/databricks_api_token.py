"""
This plugin searches for Databricks API token.
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class DatabricksApiTokenDetector(RegexBasedDetector):
    """Scans for Databricks API token."""

    secret_type = "Databricks API Token"

    denylist = [
        re.compile(r"""(?i)\b(dapi[a-h0-9]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""),
    ]
