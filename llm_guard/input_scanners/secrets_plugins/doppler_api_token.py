"""
This plugin searches for Doppler API tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class DopplerApiTokenDetector(RegexBasedDetector):
    """Scans for Doppler API Tokens."""

    secret_type = "Doppler API Token"

    denylist = [
        # Doppler API token
        re.compile(r"""(?i)dp\.pt\.[a-z0-9]{43}"""),
    ]
