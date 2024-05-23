from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, cast

from llm_guard.util import get_logger, lazy_load_dep
from llm_guard.vault import Vault

from .base import Scanner

LOGGER = get_logger()

if TYPE_CHECKING:
    import fuzzysearch


class MatchingStrategy(Enum):
    """
    An enum for the different matching strategies used to find placeholders in the model output.
    """

    EXACT = "exact"
    CASE_INSENSITIVE = "case_insensitive"
    FUZZY = "fuzzy"
    COMBINED_EXACT_FUZZY = "combined_exact_fuzzy"

    @staticmethod
    def _match_exact(text: str, vault_items: list[tuple]) -> str:
        """
        Replaces placeholders in the model output with real values from the vault.

        Parameters:
            text: The model output.
            vault_items: The list of items in the vault.
        """
        for vault_item in vault_items:
            LOGGER.debug("Replaced placeholder with real value", placeholder=vault_item[0])
            text = text.replace(vault_item[0], vault_item[1])

        return text

    @staticmethod
    def _match_case_insensitive(text: str, vault_items: list[tuple]) -> str:
        """
        It replaces all the anonymized entities with the original ones
        irrespective of their letter case.

        Examples of matching:
            keanu reeves -> Keanu Reeves
            JOHN F. KENNEDY -> John F. Kennedy

        Parameters:
            text (str): The model output.
            vault_items (List[Tuple]): The list of items in the vault.
        """
        for vault_item in vault_items:
            LOGGER.debug("Replaced placeholder with real value", placeholder=vault_item[0])
            # Use regular expressions for case-insensitive matching and replacing
            text = re.sub(vault_item[0], vault_item[1], text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def _match_fuzzy(text: str, vault_items: list[tuple], max_l_dist: int = 3) -> str:
        """
        It uses fuzzy matching to find the position of the anonymized entity in the text.
        It replaces all the anonymized entities with the original ones.

        Examples of matching:
            Kaenu Reves -> Keanu Reeves
            John F. Kennedy -> John Kennedy

        Parameters:
            text (str): The model output.
            vault_items (List[Tuple]): The list of items in the vault.
        """

        fuzzysearch = cast("fuzzysearch", lazy_load_dep("fuzzysearch"))

        for vault_item in vault_items:
            LOGGER.debug("Replaced placeholder with real value", placeholder=vault_item[0])

            matches = fuzzysearch.find_near_matches(vault_item[0], text, max_l_dist=max_l_dist)

            new_text = ""
            last_end = 0
            for m in matches:
                # add the text that isn't part of a match
                new_text += text[last_end : m.start]
                # add the replacement text
                new_text += vault_item[1]
                last_end = m.end
            # add the remaining text that wasn't part of a match
            new_text += text[last_end:]
            text = new_text

        return text

    def match(self, text: str, vault_items: list[tuple]) -> str:
        if self == MatchingStrategy.EXACT:
            return self._match_exact(text, vault_items)

        if self == MatchingStrategy.CASE_INSENSITIVE:
            return self._match_case_insensitive(text, vault_items)

        if self == MatchingStrategy.FUZZY:
            return self._match_fuzzy(text, vault_items)

        if self == MatchingStrategy.COMBINED_EXACT_FUZZY:
            text = self._match_exact(text, vault_items)
            text = self._match_fuzzy(text, vault_items)
            return text

        return text


class Deanonymize(Scanner):
    """
    A class for replacing placeholders in the model output with real values from a vault.

    This class uses the Vault class to access stored values and replaces any placeholders
    in the model's output with their corresponding values from the vault.
    """

    def __init__(
        self,
        vault: Vault,
        *,
        matching_strategy: MatchingStrategy | str = MatchingStrategy.EXACT,
    ) -> None:
        """
        Initializes an instance of the Deanonymize class.

        Parameters:
            vault (Vault): An instance of the Vault class which stores the real values.
            matching_strategy (MatchingStrategy): The strategy used to find placeholders in the model output. Defaults to the exact matching.
        """
        if isinstance(matching_strategy, str):
            matching_strategy = MatchingStrategy(matching_strategy)

        self._vault = vault
        self._matching_strategy = matching_strategy

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        vault_items = self._vault.get()
        if len(vault_items) == 0:
            LOGGER.warning("No items found in the Vault")

        output = self._matching_strategy.match(output, vault_items)

        return output, True, 0.0
