import logging
import os
import re
from typing import List, Optional

from llm_guard.input_scanners.ban_substrings import allowed_match_type

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
    ):
        """
        Initializes BanSubstrings with a match type, case sensitivity option, and a list of substrings.

        Parameters:
            match_type (str): The type of substring matching. Can be either 'str' or 'word'. Default is 'str'.
            case_sensitive (bool): Determines whether the substring matching is case sensitive. Default is False.
            substrings (Optional[List[str]]): The list of substrings to be banned from the text. Default is None.

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

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        match = False
        matched_substrings = []
        for s in self._substrings:
            if self._case_sensitive:
                s, output = s.lower(), output.lower()

            if self._match_type == "str":
                if s in output:
                    match = True
                    matched_substrings.append(s)
            elif self._match_type == "word":
                if re.search(r"\b" + s + r"\b", output):
                    match = True
                    matched_substrings.append(s)

        if match:
            log.warning(f"Found the following banned substrings: {matched_substrings}")
            return output, False, 1.0

        log.debug("No banned substrings found")

        return output, True, 0.0
