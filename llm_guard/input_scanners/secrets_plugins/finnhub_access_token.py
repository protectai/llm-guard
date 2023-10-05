"""
This plugin searches for Finnhub Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class FinnhubAccessTokenDetector(RegexBasedDetector):
    """Scans for Finnhub Access Tokens."""

    secret_type = "Finnhub Access Token"

    denylist = [
        # Finnhub Access Token
        re.compile(
            r"""(?i)(?:finnhub)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{20})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
