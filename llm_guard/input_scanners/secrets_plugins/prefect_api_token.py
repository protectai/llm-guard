"""
This plugin searches for Prefect API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class PrefectApiTokenDetector(RegexBasedDetector):
    """Scans for Prefect API Tokens."""

    secret_type = "Prefect API Token"

    denylist = [re.compile(r"""(?i)\b(pnu_[a-z0-9]{36})(?:['|\"|\n|\r|\s|\x60|;]|$)""")]
