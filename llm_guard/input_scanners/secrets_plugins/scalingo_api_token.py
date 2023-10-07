"""
This plugin searches for Scalingo API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class ScalingoApiTokenDetector(RegexBasedDetector):
    """Scans for Scalingo API Tokens."""

    secret_type = "Scalingo API Token"

    denylist = [re.compile(r"""\btk-us-[a-zA-Z0-9-_]{48}\b""")]
