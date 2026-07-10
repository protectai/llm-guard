import re
from enum import Enum
from typing import List, Pattern

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from llm_guard.util import get_logger
from llm_guard.vault import Vault

from .base import Scanner

LOGGER = get_logger()


class MatchType(Enum):
    SEARCH = "search"
    FULL_MATCH = "fullmatch"
    ALL = "all"

    def match(self, pattern: Pattern[str], text: str) -> List[re.Match[str]]:
        if self.value == "all":
            return list(pattern.finditer(text))[::-1]  # Reverse order to avoid index issues

        m = None
        if self.value == "search":
            m = pattern.search(text)

        if self.value == "fullmatch":
            m = pattern.fullmatch(text)

        if m is None:
            return []

        return [m]


class Regex(Scanner):
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class relies on the list of regular expressions provided by the user. If any of the patterns
    matches the output, the output is considered invalid. It is also possible to redact the output.
    """

    def __init__(
        self,
        patterns: list[str],
        *,
        is_blocked: bool = True,
        match_type: MatchType | str = MatchType.ALL,
        redact: bool = True,
        vault: Vault | None = None,
    ) -> None:
        """
        Initializes an instance of the Regex class.

        Parameters:
            patterns (Sequence[str]): A list of regular expressions to use for pattern matching.
            is_blocked (bool): Whether the patterns are blocked or allowed.
            match_type (str): The type of match to use.
            redact (bool): Whether to redact the output or not.
            vault (Vault): Optional vault instance to store redacted values for later deanonymization.

        Raises:
            ValueError: If no patterns are provided or both good and bad patterns are provided.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._patterns = []
        for pattern in patterns:
            self._patterns.append(re.compile(pattern))

        self._match_type = match_type
        self._is_blocked = is_blocked
        self._redact = redact
        self._vault = vault

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        regex_counter = self._get_next_regex_counter() if self._vault else 1

        # Collect all matches first
        all_matches = []
        for pattern in self._patterns:
            matches = self._match_type.match(pattern, prompt)
            if matches:
                all_matches.extend(matches)

        if not all_matches:
            if self._is_blocked:
                LOGGER.debug("None of the patterns were found in the text")
                return text_replace_builder.output_text, True, -1.0
            else:
                LOGGER.warning("None of the patterns matched the text")
                return text_replace_builder.output_text, False, 1.0

        # Sort matches by start position in reverse order for proper text replacement
        all_matches.sort(key=lambda x: x.start(), reverse=True)

        if self._is_blocked:
            LOGGER.warning("Patterns were detected in the text", num_matches=len(all_matches))

            if self._redact:
                for match in all_matches:
                    matched_text = text_replace_builder.get_text_in_position(
                        match.start(), match.end()
                    )

                    # Use vault-specific placeholders only when vault is provided
                    if self._vault:
                        placeholder = f"[REDACTED_REGEX_{regex_counter}]"
                        if not self._vault.placeholder_exists(placeholder):
                            self._vault.append((placeholder, matched_text))
                        regex_counter += 1
                    else:
                        # Maintain backward compatibility
                        placeholder = "[REDACTED]"

                    text_replace_builder.replace_text_get_insertion_index(
                        placeholder,
                        match.start(),
                        match.end(),
                    )

            return text_replace_builder.output_text, False, 1.0

        LOGGER.debug("Patterns matched the text", num_matches=len(all_matches))
        return text_replace_builder.output_text, True, -1.0

    def _get_next_regex_counter(self) -> int:
        """Get the next available counter for regex placeholders."""
        if not self._vault:
            return 1

        existing_indices = set()
        for placeholder, _ in self._vault.get():
            if placeholder.startswith("[REDACTED_REGEX_") and placeholder.endswith("]"):
                try:
                    index = int(placeholder.split("_")[-1][:-1])
                    existing_indices.add(index)
                except ValueError:
                    pass

        counter = 1
        while counter in existing_indices:
            counter += 1
        return counter
