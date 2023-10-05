"""
This plugin searches for Flickr Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class FlickrAccessTokenDetector(RegexBasedDetector):
    """Scans for Flickr Access Tokens."""

    secret_type = "Flickr Access Token"

    denylist = [
        # Flickr Access Token
        re.compile(
            r"""(?i)(?:flickr)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{32})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
