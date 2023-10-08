import logging
import os
from typing import List, Optional

from llm_guard.input_scanners.ban_substrings import BanSubstrings as InputBanSubstrings

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
        match_type: str = "str",
        case_sensitive: bool = False,
        substrings: Optional[List[str]] = None,
        redact: bool = False,
        contains_all: bool = False,  # contains any
    ):
        """
        Initializes BanSubstrings with a match type, case sensitivity option, and a list of substrings.

        Parameters:
            match_type (str): The type of substring matching. Can be either 'str' or 'word'. Default is 'str'.
            case_sensitive (bool): Determines whether the substring matching is case sensitive. Default is False.
            substrings (Optional[List[str]]): The list of substrings to be banned from the text. Default is None.
            redact (bool): Determines whether the banned substrings should be redacted from the text. Default is False.
            contains_all (bool): Flag to indicate if need to match all substrings instead of any of them. Default is contains any.

        Raises:
            ValueError: If no substrings are provided or match_type is not 'str' or 'word'.
        """

        self._scanner = InputBanSubstrings(
            match_type=match_type,
            case_sensitive=case_sensitive,
            substrings=substrings,
            redact=redact,
            contains_all=contains_all,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
