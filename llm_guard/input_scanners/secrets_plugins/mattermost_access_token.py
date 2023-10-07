"""
This plugin searches for Mattermost Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class MattermostAccessTokenDetector(RegexBasedDetector):
    """Scans for Mattermost Access Tokens."""

    secret_type = "Mattermost Access Token"

    denylist = [
        # Mattermost Access Token
        re.compile(
            r"""(?i)(?:mattermost)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{26})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
