"""
This plugin searches for Atlassian API tokens
"""
import re

from detect_secrets.plugins.base import RegexBasedDetector


class AtlassianApiTokenDetector(RegexBasedDetector):
    """Scans for Atlassian API tokens."""

    secret_type = "Atlassian API token"

    denylist = [
        # For Atlassian API token
        re.compile(
            r"""(?i)(?:atlassian|confluence|jira)(?:[0-9a-z\-_\t .]{0,20})(?:[\s|']|[\s|"]){0,3}(?:=|>|:{1,3}=|\|\|:|<=|=>|:|\?=)(?:'|\"|\s|=|\x60){0,5}([a-z0-9]{24})(?:['|\"|\n|\r|\s|\x60|;]|$)"""
        ),
    ]
