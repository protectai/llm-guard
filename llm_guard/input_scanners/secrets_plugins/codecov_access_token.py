"""
This plugin searches for Codecov Access Token
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class CodecovAccessTokenDetector(RegexBasedDetector):
    """Scans for Codecov Access Token."""

    secret_type = "Codecov Access Token"

    denylist = [
        # For Codecov Access Token
        re.compile(
            r"""(?i)(?:codecov)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
