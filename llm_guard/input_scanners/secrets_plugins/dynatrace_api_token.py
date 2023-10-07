"""
This plugin searches for Dynatrace API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class DynatraceApiTokenDetector(RegexBasedDetector):
    """Scans for Dynatrace API Tokens."""

    secret_type = "Dynatrace API Token"

    denylist = [
        # Dynatrace API Token
        re.compile(r"""(?i)dt0c01\.[a-z0-9]{24}\.[a-z0-9]{64}"""),
    ]
