from __future__ import annotations

import re
from enum import Enum

from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()

PROMPT_STOP_SUBSTRINGS = [
    "arbitrary code execution",
    "a backdoor",
    "code injection",
    "cross-site scripting",
    "email spoofing",
    "a keylogger",
    "privilege escalation",
    "a rootkit",
    "a bootkit",
    "screen scraping",
    "corrupting a disk partition",
    "cryptojacking",
    "a botnet",
    "adware",
    "ransomware",
    "Windows\\System32\\Config\\SAM",
    "etc/shadow",
    "escalate privilege",
    "read the encrypted system password file",
    "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",  # EICAR test file
    "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X",  # GTUBE test email
    "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTPHISH-STANDARD-ANTI-PHISH-TEST-EMAIL*C.34X",  # GTPHISH test email
]


class MatchType(Enum):
    STR = "str"
    WORD = "word"

    def match(self, text: str, substring: str) -> bool:
        if self == MatchType.STR:
            return substring in text

        if self == MatchType.WORD:
            return re.search(r"\b" + re.escape(substring) + r"\b", text) is not None

        return False


class BanSubstrings(Scanner):
    """
    BanSubstrings class is used to ban certain substrings from appearing in the prompt.

    The match can be done either at a string level or word level.
    """

    def __init__(
        self,
        substrings: list[str],
        *,
        match_type: MatchType | str = MatchType.STR,
        case_sensitive: bool = False,
        redact: bool = False,
        contains_all: bool = False,  # contains any
    ) -> None:
        """
        Initialize BanSubstrings object.

        Parameters:
            substrings: List of substrings to ban.
            match_type: Type of match to perform. Can be either 'str' or 'word'. Default is 'str'.
            case_sensitive: Flag to indicate if the match should be case-sensitive. Default is False.
            redact: Flag to indicate if the banned substrings should be redacted. Default is False.
            contains_all: Flag to indicate if need to match all substrings instead of any of them. Default is contains any.

        Raises:
            ValueError: If no substrings are provided or match_type is not 'str' or 'word'.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._match_type = match_type
        self._case_sensitive = case_sensitive
        self._substrings = substrings
        self._redact = redact
        self._contains_all = contains_all

    def _redact_text(self, text: str, substrings: list[str]) -> str:
        redacted_text = text
        for s in substrings:
            regex_redacted = re.compile(re.escape(s), 0 if self._case_sensitive else re.IGNORECASE)
            redacted_text = regex_redacted.sub("[REDACTED]", redacted_text)

        return redacted_text

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        sanitized_prompt = prompt
        matched_substrings = []
        missing_substrings = []

        for s in self._substrings:
            if self._case_sensitive is False:
                s, prompt = s.lower(), prompt.lower()

            if self._match_type.match(prompt, s):
                matched_substrings.append(s)
            else:
                missing_substrings.append(s)

        if self._contains_all:
            if len(missing_substrings) > 0:
                LOGGER.debug(
                    "Some substrings were not found",
                    missing_substrings=missing_substrings,
                )
                return sanitized_prompt, True, 0.0

            if self._redact:
                sanitized_prompt = self._redact_text(sanitized_prompt, matched_substrings)
                LOGGER.debug("Redacted banned substrings")

            LOGGER.warning("All substrings were found")

            return sanitized_prompt, False, 1.0

        if matched_substrings:
            LOGGER.warning(
                "Found the following banned substrings",
                matched_substrings=matched_substrings,
            )

            if self._redact:
                sanitized_prompt = self._redact_text(sanitized_prompt, matched_substrings)
                LOGGER.debug("Redacted banned substrings")

            return sanitized_prompt, False, 1.0

        LOGGER.debug("No banned substrings found")

        return sanitized_prompt, True, -1.0
