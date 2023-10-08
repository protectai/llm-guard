import os
import re
from typing import List

from llm_guard.util import logger

from .base import Scanner

stop_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "resources",
    "prompt_stop_substrings.json",
)

MATCH_TYPE_STR = "str"
MATCH_TYPE_WORD = "word"
allowed_match_type = [MATCH_TYPE_STR, MATCH_TYPE_WORD]


class BanSubstrings(Scanner):
    """
    BanSubstrings class is used to ban certain substrings from appearing in the prompt.

    The match can be done either at a string level or word level.
    """

    def __init__(
        self,
        match_type: str = MATCH_TYPE_STR,
        case_sensitive: bool = False,
        substrings: List[str] = None,
        redact: bool = False,
        contains_all: bool = False,  # contains any
    ):
        """
        Initialize BanSubstrings object.

        Args:
            match_type (str, optional): The type of match to be performed. Either 'str' or 'word'.
                                        'str' means the match is performed at the string level and 'word' means the match is done at the word level.
                                        Default is 'str'.
            case_sensitive (bool, optional): Flag to indicate if the match should be case-sensitive. Default is False.
            substrings (List[str], optional): List of substrings to ban.
            redact (bool, optional): Flag to indicate if the banned substrings should be redacted. Default is False.
            contains_all (bool): Flag to indicate if need to match all substrings instead of any of them. Default is contains any.

        Raises:
            ValueError: If no substrings are provided or match_type is not 'str' or 'word'.
        """

        if not substrings:
            raise ValueError("No substrings provided")

        if match_type not in allowed_match_type:
            raise ValueError(f"This match_type is not recognized. Allowed: {allowed_match_type}")

        self._match_type = match_type  # str or word
        self._case_sensitive = case_sensitive
        self._substrings = substrings
        self._redact = redact
        self._contains_all = contains_all

    @staticmethod
    def _redact_text(text: str, substrings: List[str]) -> str:
        redacted_text = text
        for s in substrings:
            redacted_text = redacted_text.replace(s, "[REDACTED]")
        return redacted_text

    def scan(self, prompt: str) -> (str, bool, float):
        matched_substrings = []
        missing_substrings = []
        for s in self._substrings:
            if self._case_sensitive:
                s, prompt = s.lower(), prompt.lower()

            if self._match_type == MATCH_TYPE_STR:
                if s in prompt:
                    matched_substrings.append(s)
                else:
                    missing_substrings.append(s)

            if self._match_type == MATCH_TYPE_WORD:
                if re.search(r"\b" + s + r"\b", prompt):
                    matched_substrings.append(s)
                else:
                    missing_substrings.append(s)

        if self._contains_all:
            if len(missing_substrings) > 0:
                logger.debug(f"Some substrings were not found: " + ", ".join(missing_substrings))
                return prompt, True, 0.0

            if self._redact:
                prompt = self._redact_text(prompt, matched_substrings)
                logger.debug("Redacted banned substrings")

            logger.warning(f"All substrings were found")

            return prompt, False, 1.0

        if matched_substrings:
            logger.warning(
                f"Found the following banned substrings: " + ", ".join(matched_substrings)
            )

            if self._redact:
                prompt = self._redact_text(prompt, matched_substrings)
                logger.debug("Redacted banned substrings")

            return prompt, False, 1.0

        logger.debug("No banned substrings found")

        return prompt, True, 0.0
