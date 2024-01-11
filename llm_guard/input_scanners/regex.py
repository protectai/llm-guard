import re
from enum import Enum
from typing import List, Match, Pattern

from llm_guard.util import logger

from .base import Scanner


class MatchType(Enum):
    SEARCH = "search"
    FULL_MATCH = "fullmatch"

    def match(self, pattern: Pattern[str], text: str):
        return getattr(pattern, self.value)(text)


class Regex(Scanner):
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class relies on the list of regular expressions provided by the user. If any of the patterns
    matches the output, the output is considered invalid. It is also possible to redact the output.
    """

    def __init__(
        self,
        patterns: List[str],
        is_blocked: bool = True,
        match_type: MatchType = MatchType.SEARCH,
        redact: bool = True,
    ):
        """
        Initializes an instance of the Regex class.

        Parameters:
            patterns (List[str]): A list of regular expressions to use for pattern matching.
            is_blocked (bool): Whether the patterns are blocked or allowed.
            match_type (str): The type of match to use. Can be either "search" or "fullmatch".
            redact (bool): Whether to redact the output or not.

        Raises:
            ValueError: If no patterns provided or both good and bad patterns provided.
        """

        assert len(patterns) > 0, "no patterns provided"

        self._patterns = []
        for pattern in patterns:
            self._patterns.append(re.compile(pattern))

        self._match_type = match_type
        self._is_blocked = is_blocked
        self._redact = redact

    @staticmethod
    def _redact_match(text: str, match: Match):
        return text[: match.start()] + "[REDACTED]" + text[match.end() :]

    def scan(self, prompt: str) -> (str, bool, float):
        sanitized_prompt = prompt

        for pattern in self._patterns:
            match = self._match_type.match(pattern, prompt)
            if match is None:
                continue

            if self._is_blocked:
                logger.warning(f"Pattern {pattern} was detected in the text")

                if self._redact:
                    sanitized_prompt = self._redact_match(sanitized_prompt, match)

                return sanitized_prompt, False, 1.0

            logger.debug(f"Pattern {pattern} matched the text")
            return prompt, True, 0.0

        if self._is_blocked:
            logger.debug(f"None of the patterns were found in the text")
            return prompt, True, 0.0

        logger.warning(f"None of the patterns matched the text")
        return prompt, False, 1.0
