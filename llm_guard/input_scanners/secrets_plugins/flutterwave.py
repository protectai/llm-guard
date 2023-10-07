"""
This plugin searches for Flutterwave API keys.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class FlutterwaveDetector(RegexBasedDetector):
    """Scans for Flutterwave API Keys."""

    secret_type = "Flutterwave API Key"

    denylist = [
        # Flutterwave Encryption Key
        re.compile(r"""(?i)FLWSECK_TEST-[a-h0-9]{12}"""),
        # Flutterwave Public Key
        re.compile(r"""(?i)FLWPUBK_TEST-[a-h0-9]{32}-X"""),
        # Flutterwave Secret Key
        re.compile(r"""(?i)FLWSECK_TEST-[a-h0-9]{32}-X"""),
    ]
