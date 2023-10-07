"""
This plugin searches for Pulumi API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class PulumiApiTokenDetector(RegexBasedDetector):
    """Scans for Pulumi API Tokens."""

    secret_type = "Pulumi API Token"

    denylist = [re.compile(r"""(?i)\b(pul-[a-f0-9]{40})(?:['|\"|\n|\r|\s|\x60|;]|$)""")]
