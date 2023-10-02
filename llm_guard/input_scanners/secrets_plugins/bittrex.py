"""
This plugin searches for Bittrex Access Key and Secret Key
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class BittrexDetector(RegexBasedDetector):
    """Scans for Bittrex Access Key and Secret Key."""

    secret_type = "Bittrex Secrets"

    denylist = [
        # For Bittrex Access Key
        re.compile(
            r"""(?i)(?:bittrex)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
        # For Bittrex Secret Key
        re.compile(
            r"""(?i)(?:bittrex)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
