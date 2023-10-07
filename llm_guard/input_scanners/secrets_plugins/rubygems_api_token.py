"""
This plugin searches for Rubygem API Tokens.
"""

import re

from detect_secrets.plugins.base import RegexBasedDetector


class RubygemsApiTokenDetector(RegexBasedDetector):
    """Scans for Rubygem API Tokens."""

    secret_type = "Rubygem API Token"

    denylist = [re.compile(r"""(?i)\b(rubygems_[a-f0-9]{48})(?:['|\"|\n|\r|\s|\x60|;]|$)""")]
