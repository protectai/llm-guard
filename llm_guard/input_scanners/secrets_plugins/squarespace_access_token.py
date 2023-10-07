"""
This plugin searches for Squarespace Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class SquarespaceAccessTokenDetector(RegexBasedDetector):
    """Scans for Squarespace Access Tokens."""

    secret_type = "Squarespace Access Token"

    denylist = [
        re.compile(
            r"""(?i)(?:squarespace)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        )
    ]
