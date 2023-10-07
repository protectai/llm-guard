"""
This plugin searches for Shippo API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class ShippoApiTokenDetector(RegexBasedDetector):
    """Scans for Shippo API Tokens."""

    secret_type = "Shippo API Token"

    denylist = [
        re.compile(r"""(?i)\b(shippo_(live|test)_[a-f0-9]{40})(?:['|\"|\n|\r|\s|\x60|;]|$)""")
    ]
