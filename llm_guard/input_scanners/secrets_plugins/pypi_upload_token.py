"""
This plugin searches for PyPI Upload Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class PyPiUploadTokenDetector(RegexBasedDetector):
    """Scans for PyPI Upload Tokens."""

    secret_type = "PyPI Upload Token"

    denylist = [re.compile(r"""pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\-_]{50,1000}""")]
