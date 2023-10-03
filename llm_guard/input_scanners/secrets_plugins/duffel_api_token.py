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
        re.compile(r"""duffel_(test|live)_(?i)[a-z0-9_\-=]{43}"""),
    ]
