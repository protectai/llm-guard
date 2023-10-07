"""
This plugin searches for Zendesk Secret Keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class ZendeskSecretKeyDetector(RegexBasedDetector):
    """Scans for Zendesk Secret Keys."""

    secret_type = "Zendesk Secret Key"

    denylist = [
        re.compile(
            r"""(?i)(?:zendesk)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{40})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        )
    ]
