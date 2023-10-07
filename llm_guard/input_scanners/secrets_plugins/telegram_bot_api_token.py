"""
This plugin searches for Telegram Bot API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class TelegramBotApiTokenDetector(RegexBasedDetector):
    """Scans for Telegram Bot API Tokens."""

    secret_type = "Telegram Bot API Token"

    denylist = [
        re.compile(r"""(?i)(?:^|[^0-9])([0-9]{5,16}:A[a-zA-Z0-9_\-]{34})(?:$|[^a-zA-Z0-9_\-])""")
    ]
