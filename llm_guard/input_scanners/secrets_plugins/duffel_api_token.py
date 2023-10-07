"""
This plugin searches for Duffel API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class DuffelApiTokenDetector(RegexBasedDetector):
    """Scans for Duffel API Tokens."""

    secret_type = "Duffel API Token"

    denylist = [
        # Duffel API Token
        re.compile(r"""(?i)duffel_(test|live)_[a-z0-9_\-=]{43}"""),
    ]
