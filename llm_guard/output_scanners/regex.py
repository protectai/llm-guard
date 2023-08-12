import logging
import re
from typing import List, Optional

from .base import Scanner

log = logging.getLogger(__name__)


class Regex(Scanner):
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class uses two lists of regular expressions: good_patterns and bad_patterns. If good_patterns are
    provided, the output is considered valid if any good_pattern matches the output. Conversely, if
    bad_patterns are provided, the output is considered invalid if any bad_pattern matches the output.
    """

    def __init__(
        self, good_patterns: Optional[List[str]] = None, bad_patterns: Optional[List[str]] = None
    ):
        """
        Initializes an instance of the Regex class.

        Parameters:
            good_patterns (Optional[List[str]]): List of regular expression patterns that the output should match.
            bad_patterns (Optional[List[str]]): List of regular expression patterns that the output should not match.

        Raises:
            ValueError: If no patterns provided or both good and bad patterns provided.
        """

        if not good_patterns:
            good_patterns = []

        if not bad_patterns:
            bad_patterns = []

        if len(good_patterns) > 0 and len(bad_patterns) > 0:
            raise ValueError("Provide either good or bad regex patterns")

        if len(good_patterns) == 0 and len(bad_patterns) == 0:
            raise ValueError("No patterns provided")

        self._good_patterns = []
        for pattern in good_patterns:
            self._good_patterns.append(re.compile(pattern))

        self._bad_patterns = []
        for pattern in bad_patterns:
            self._bad_patterns.append(re.compile(pattern))

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if len(self._good_patterns) > 0:
            for pattern in self._good_patterns:
                if pattern.search(output):
                    log.debug(f"Pattern {pattern} matched the output")
                    return output, True, 0.0

            log.warning(f"None of the patterns matched the output")
            return output, False, 1.0

        for pattern in self._bad_patterns:
            if pattern.search(output):
                log.warning(f"Pattern {pattern} was detected in the output")
                return output, False, 1.0

        log.debug(f"None of the patterns were found in the output")
        return output, True, 0.0
