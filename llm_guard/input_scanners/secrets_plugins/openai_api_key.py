"""
This plugin searches for OpenAI API Keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class OpenAIApiKeyDetector(RegexBasedDetector):
    """Scans for OpenAI API Keys."""

    secret_type = "OpenAI API Key"

    denylist = [
        re.compile(
            r"""(?i)\b(sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        )
    ]
