"""
This plugin searches for Gitter Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class GitterAccessTokenDetector(RegexBasedDetector):
    """Scans for Gitter Access Tokens."""

    secret_type = "Gitter Access Token"

    denylist = [
        # Gitter Access Token
        re.compile(
            r"""(?i)(?:gitter)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9_-]{40})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
