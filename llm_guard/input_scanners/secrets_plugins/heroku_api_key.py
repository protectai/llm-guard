"""
This plugin searches for Heroku API Keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class HerokuApiKeyDetector(RegexBasedDetector):
    """Scans for Heroku API Keys."""

    secret_type = "Heroku API Key"

    denylist = [
        re.compile(
            r"""(?i)(?:heroku)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
