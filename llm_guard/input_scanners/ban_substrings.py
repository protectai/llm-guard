import logging
import os
import re
from typing import List

from .base import Scanner

log = logging.getLogger(__name__)
stop_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "resources",
    "prompt_stop_substrings.json",
)
allowed_match_type = ["str", "word"]


class BanSubstrings(Scanner):
    """
    BanSubstrings class is used to ban certain substrings from appearing in the prompt.

    The match can be done either at a string level or word level.
    """

    def __init__(
        self,
        match_type: str = "str",
        case_sensitive: bool = False,
        substrings: List[str] = None,
    ):
        """
        Initialize BanSubstrings object.

        Args:
            match_type (str, optional): The type of match to be performed. Either 'str' or 'word'.
                                        'str' means the match is performed at the string level and 'word' means the match is done at the word level.
                                        Default is 'str'.
            case_sensitive (bool, optional): Flag to indicate if the match should be case-sensitive. Default is False.
            substrings (List[str], optional): List of substrings to ban.
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

    def scan(self, prompt: str) -> (str, bool, float):
        match = False
        matched_substrings = []
        for s in self._substrings:
            if self._case_sensitive:
                s, prompt = s.lower(), prompt.lower()

            if self._match_type == "str":
                if s in prompt:
                    match = True
                    matched_substrings.append(s)
            elif self._match_type == "word":
                if re.search(r"\b" + s + r"\b", prompt):
                    match = True
                    matched_substrings.append(s)

        if match:
            log.warning(f"Found the following banned substrings: {matched_substrings}")
            return prompt, False, 1.0

        log.debug("No banned substrings found")

        return prompt, True, 0.0
