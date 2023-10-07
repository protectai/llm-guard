"""
This plugin searches for SendGrid API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class SendGridApiTokenDetector(RegexBasedDetector):
    """Scans for SendGrid API Tokens."""

    secret_type = "SendGrid API Token"

    denylist = [re.compile(r"""(?i)\b(SG\.[a-z0-9=_\-\.]{66})(?:['|\"|\n|\r|\s|\x60|;]|$)""")]
