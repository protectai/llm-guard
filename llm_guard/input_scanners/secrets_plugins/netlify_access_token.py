"""
This plugin searches for Netlify Access Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class NetlifyAccessTokenDetector(RegexBasedDetector):
    """Scans for Netlify Access Tokens."""

    secret_type = "Netlify Access Token"

    denylist = [
        # Netlify Access Token
        re.compile(
            r"""(?i)(?:netlify)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9=_\-]{40,46})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
