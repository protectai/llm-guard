"""
This plugin searches for Clojars API tokens
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class ClojarsApiTokenDetector(RegexBasedDetector):
    """Scans for Clojars API tokens."""

    secret_type = "Clojars API token"

    denylist = [
        # For Clojars API token
        re.compile(r"(?i)(CLOJARS_)[a-z0-9]{60}"),
    ]
