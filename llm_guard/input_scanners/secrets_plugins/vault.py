import re

from detect_secrets.plugins.base import RegexBasedDetector


class VaultDetector(RegexBasedDetector):
    """Scans for Vault Batch Tokens and Vault Service Tokens."""

    secret_type = "Vault Token"

    denylist = [
        # Vault Batch Token
        re.compile(r"""(?i)\b(hvb\.[a-z0-9_-]{138,212})(?:['|\"|\n|\r|\s|\x60|;]|$)"""),
        # Vault Service Token
        re.compile(r"""(?i)\b(hvs\.[a-z0-9_-]{90,100})(?:['|\"|\n|\r|\s|\x60|;]|$)"""),
    ]
