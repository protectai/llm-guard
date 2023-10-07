"""
This plugin searches for MapBox API tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class MapBoxApiTokenDetector(RegexBasedDetector):
    """Scans for MapBox API tokens."""

    secret_type = "MapBox API Token"

    denylist = [
        # MapBox API Token
        re.compile(
            r"""(?i)(?:mapbox)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}(pk\.[a-z0-9]{60}\.[a-z0-9]{22})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
