"""
This plugin searches for Hugging Face Access and Organization API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class HuggingFaceDetector(RegexBasedDetector):
    """Scans for Hugging Face Tokens."""

    secret_type = "Hugging Face Token"

    denylist = [
        # Hugging Face Access token
        re.compile(r"""(?:^|[\\'"` >=:])(hf_[a-zA-Z]{34})(?:$|[\\'"` <])"""),
        # Hugging Face Organization API token
        re.compile(r"""(?:^|[\\'"` >=:\(,)])(api_org_[a-zA-Z]{34})(?:$|[\\'"` <\),])"""),
    ]
