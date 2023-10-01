"""
This plugin searches for Age secret keys
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class AgeSecretKeyDetector(RegexBasedDetector):
    """Scans for Age secret keys."""

    secret_type = "Age Secret Key"

    denylist = [
        re.compile(r"""AGE-SECRET-KEY-1[QPZRY9X8GF2TVDW0S3JN54KHCE6MUA7L]{58}"""),
    ]
