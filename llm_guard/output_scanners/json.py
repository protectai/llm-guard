import json
import re

import regex

from llm_guard.util import logger

from .base import Scanner


class JSON(Scanner):
    """
    A scanner class to detect and validate JSON structures within a given output.

    It primarily serves to detect JSON objects and arrays using regular expressions
    and then to validate them to ensure their correctness.
    """

    def __init__(self, required_elements: int = 0):
        """Initialize the JSON scanner.

        Args:
            required_elements (int, optional): The minimum number of JSON elements
            that should be present. Defaults to 0.
        """
        self._required_elements = required_elements

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """Check if the input string is a valid JSON.

        Args:
            json_str (str): The input string to check.

        Returns:
            bool: True if the input string is a valid JSON, False otherwise.
        """
        try:
            json.loads(json_str)
            return True
        except ValueError:
            return False

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        # Find JSON object and array candidates using regular expressions
        json_candidates = regex.findall(r"(?<!\\)(?:\\\\)*\{(?:[^{}]|(?R))*\}", output, re.DOTALL)

        # Validate each JSON
        valid_jsons = [candidate for candidate in json_candidates if self.is_valid_json(candidate)]

        if len(valid_jsons) < self._required_elements:
            logger.warning(
                f"There should be at least {self._required_elements} JSONs but {len(valid_jsons)} found"
            )
            return output, False, 1.0

        # Compare
        if len(valid_jsons) != len(json_candidates):
            logger.warning(f"Only {len(valid_jsons)}/{len(json_candidates)} JSONs are valid")

            return output, False, 1.0

        return output, True, 0.0
