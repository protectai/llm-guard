"""
This plugin searches for Fastly API keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class FastlyApiKeyDetector(RegexBasedDetector):
    """Scans for Fastly API keys."""

    secret_type = "Fastly API Key"

    denylist = [
        # Fastly API key
        re.compile(
            r"""(?i)(?:fastly)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9=_\-]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
