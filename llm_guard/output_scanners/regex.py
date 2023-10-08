from typing import List, Optional

from llm_guard.input_scanners.regex import Regex as InputRegex

from .base import Scanner


class Regex(Scanner):
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class uses two lists of regular expressions: good_patterns and bad_patterns. If good_patterns are
    provided, the output is considered valid if any good_pattern matches the output. Conversely, if
    bad_patterns are provided, the output is considered invalid if any bad_pattern matches the output.
    """

    def __init__(
        self,
        good_patterns: Optional[List[str]] = None,
        bad_patterns: Optional[List[str]] = None,
        redact=True,
    ):
        """
        Initializes an instance of the Regex class.

        Parameters:
            good_patterns (Optional[List[str]]): List of regular expression patterns that the output should match.
            bad_patterns (Optional[List[str]]): List of regular expression patterns that the output should not match.
            redact (bool): Whether to redact the output or not.

        Raises:
            ValueError: If no patterns provided or both good and bad patterns provided.
        """

        self._scanner = InputRegex(good_patterns, bad_patterns, redact)

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
