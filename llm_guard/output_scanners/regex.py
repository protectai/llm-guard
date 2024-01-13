from typing import Sequence, Union

from llm_guard.input_scanners.regex import MatchType
from llm_guard.input_scanners.regex import Regex as InputRegex

from .base import Scanner


class Regex(Scanner):
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class relies on the list of regular expressions provided by the user. If any of the patterns
    matches the output, the output is considered invalid. It is also possible to redact the output.
    """

    def __init__(
        self,
        patterns: Sequence[str],
        *,
        is_blocked: bool = True,
        match_type: Union[MatchType, str] = MatchType.SEARCH,
        redact=True,
    ):
        """
        Initializes an instance of the Regex class.

        Parameters:
            patterns (Sequence[str]): A list of regular expressions to use for pattern matching.
            is_blocked (bool): Whether the patterns are blocked or allowed.
            match_type (str): The type of match to use. Can be either "search" or "fullmatch".
            redact (bool): Whether to redact the output or not.

        Raises:
            ValueError: If no patterns provided or both good and bad patterns provided.
        """

        self._scanner = InputRegex(
            patterns, is_blocked=is_blocked, match_type=match_type, redact=redact
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
