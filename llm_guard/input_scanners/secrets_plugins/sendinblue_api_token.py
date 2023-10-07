"""
This plugin searches for SendinBlue API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class SendinBlueApiTokenDetector(RegexBasedDetector):
    """Scans for SendinBlue API Tokens."""

    secret_type = "SendinBlue API Token"

    denylist = [
        re.compile(r"""(?i)\b(xkeysib-[a-f0-9]{64}-[a-z0-9]{16})(?:['|\"|\n|\r|\s|\x60|;]|$)""")
    ]
