from __future__ import annotations

import logging
import os

from llm_guard.input_scanners.ban_substrings import BanSubstrings as InputBanSubstrings, MatchType

from .base import Scanner

log = logging.getLogger(__name__)
stop_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "resources",
    "output_stop_substrings.json",
)


class BanSubstrings(Scanner):
    """
    A text scanner that checks whether the generated text output includes banned substrings.

    The class offers the functionality to match substrings in two different ways: as 'str' or as 'word'.
    - 'str' matches the substring anywhere in the text.
    - 'word' matches the substring as a whole word.
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
        Initializes BanSubstrings with a match type, case sensitivity option, and a list of substrings.

        Parameters:
            substrings: The list of substrings to be banned from the text.
            match_type: The type of substring matching. Can be either 'str' or 'word'. Default is 'str'.
            case_sensitive: Determines whether the substring matching is case sensitive. Default is False.
            redact: Determines whether the banned substrings should be redacted from the text. Default is False.
            contains_all: Flag to indicate if need to match all substrings instead of any of them. Default is contains any.

        Raises:
            ValueError: If no substrings are provided or match_type is not 'str' or 'word'.
        """

        self._scanner = InputBanSubstrings(
            substrings,
            match_type=match_type,
            case_sensitive=case_sensitive,
            redact=redact,
            contains_all=contains_all,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
