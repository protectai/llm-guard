"""
This plugin searches for Readme API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class ReadmeApiTokenDetector(RegexBasedDetector):
    """Scans for Readme API Tokens."""

    secret_type = "Readme API Token"

    denylist = [re.compile(r"""(?i)\b(rdme_[a-z0-9]{70})(?:['|\"|\n|\r|\s|\x60|;]|$)""")]
