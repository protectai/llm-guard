"""
This plugin searches for Beamer API tokens
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class BeamerApiTokenDetector(RegexBasedDetector):
    """Scans for Beamer API tokens."""

    secret_type = "Beamer API token"

    denylist = [
        # For Beamer API token
        re.compile(
            r"""(?i)(?:beamer)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}(b_[a-z0-9=_\-]{44})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
