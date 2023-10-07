"""
This plugin searches for Frame.io API tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class FrameIoApiTokenDetector(RegexBasedDetector):
    """Scans for Frame.io API Tokens."""

    secret_type = "Frame.io API Token"

    denylist = [
        # Frame.io API token
        re.compile(r"""(?i)fio-u-[a-z0-9\-_=]{64}"""),
    ]
