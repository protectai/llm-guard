"""
This plugin searches for Postman API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class PostmanApiTokenDetector(RegexBasedDetector):
    """Scans for Postman API Tokens."""

    secret_type = "Postman API Token"

    denylist = [
        re.compile(r"""(?i)\b(PMAK-[a-f0-9]{24}-[a-f0-9]{34})(?:['|\"|\n|\r|\s|\x60|;]|$)""")
    ]
