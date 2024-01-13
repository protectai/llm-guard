import re
from enum import Enum
from typing import Pattern, Sequence, Union

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

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
        patterns: Sequence[str],
        *,
        is_blocked: bool = True,
        match_type: Union[MatchType, str] = MatchType.SEARCH,
        redact: bool = True,
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
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._patterns = []
        for pattern in patterns:
            self._patterns.append(re.compile(pattern))

        self._match_type = match_type
        self._is_blocked = is_blocked
        self._redact = redact

    def scan(self, prompt: str) -> (str, bool, float):
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        for pattern in self._patterns:
            match = self._match_type.match(pattern, prompt)
            if match is None:
                continue

            if self._is_blocked:
                logger.warning(f"Pattern {pattern} was detected in the text")

                if self._redact:
                    text_replace_builder.replace_text_get_insertion_index(
                        "[REDACTED]",
                        match.start(),
                        match.end(),
                    )

                return text_replace_builder.output_text, False, 1.0

            logger.debug(f"Pattern {pattern} matched the text")
            return text_replace_builder.output_text, True, 0.0

        if self._is_blocked:
            logger.debug(f"None of the patterns were found in the text")
            return text_replace_builder.output_text, True, 0.0

        logger.warning(f"None of the patterns matched the text")
        return text_replace_builder.output_text, False, 1.0
