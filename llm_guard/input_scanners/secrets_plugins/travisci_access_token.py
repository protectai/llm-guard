"""
This plugin searches for Travis CI Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class TravisCiAccessTokenDetector(RegexBasedDetector):
    """Scans for Travis CI Access Tokens."""

    secret_type = "Travis CI Access Token"

    denylist = [
        re.compile(
            r"""(?i)(?:travis)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{22})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        )
    ]
