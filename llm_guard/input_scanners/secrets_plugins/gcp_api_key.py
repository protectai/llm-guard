"""
This plugin searches for GCP API keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class GCPApiKeyDetector(RegexBasedDetector):
    """Scans for GCP API keys."""

    secret_type = "GCP API Key"

    denylist = [
        # GCP API Key
        re.compile(r"""(?i)\b(AIza[0-9A-Za-z\\-_]{35})(?:['|\"|\n|\r|\s|\x60|;]|$)"""),
    ]
