"""
This plugin searches for EasyPost tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class EasyPostDetector(RegexBasedDetector):
    """Scans for various EasyPost Tokens."""

    secret_type = "EasyPost Token"

    denylist = [
        # EasyPost API token
        re.compile(r"""(?i)\bEZAK[a-z0-9]{54}"""),
        # EasyPost test API token
        re.compile(r"""(?i)\bEZTK[a-z0-9]{54}"""),
    ]
