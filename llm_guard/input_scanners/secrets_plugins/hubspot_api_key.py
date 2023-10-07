"""
This plugin searches for HubSpot API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class HubSpotApiTokenDetector(RegexBasedDetector):
    """Scans for HubSpot API Tokens."""

    secret_type = "HubSpot API Token"

    denylist = [
        # HubSpot API Token
        re.compile(
            r"""(?i)(?:hubspot)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
