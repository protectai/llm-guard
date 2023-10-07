"""
This plugin searches for Algolia API keys
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class AlgoliaApiKeyDetector(RegexBasedDetector):
    """Scans for Algolia API keys."""

    secret_type = "Algolia API Key"

    denylist = [
        re.compile(r"""(?i)\b((LTAI)[a-z0-9]{20})(?:['|\"|\n|\r|\s|\x60|;]|$)"""),
    ]
