import json
import re

import regex

from llm_guard.util import lazy_load_dep, logger

from .base import Scanner


class JSON(Scanner):
    """
    A scanner class to detect, validate and repair JSON structures within a given output.

    It primarily serves to detect JSON objects and arrays using regular expressions,
    then to validate them to ensure their correctness and finally to repair them if necessary.
    """

    def __init__(self, required_elements: int = 0, repair: bool = True):
        """Initialize the JSON scanner.

        Args:
            required_elements (int, optional): The minimum number of JSON elements
            that should be present. Defaults to 0.
            repair (bool, optional): Whether to repair the broken JSON. Defaults to False.
        """
        self._required_elements = required_elements
        self._repair = repair

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

    @staticmethod
    def repair_json(json_str: str) -> str:
        """Repair a broken JSON string.

        Args:
            json_str (str): The input string to repair.

        Returns:
            str: The repaired JSON string.
        """

        json_repair = lazy_load_dep("json_repair")
        try:
            repaired_json = json_repair.repair_json(
                json_str, skip_json_loads=True, return_objects=False
            )
        except ValueError:
            return json_str

        return repaired_json

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        # Find JSON object and array candidates using regular expressions
        json_candidates = regex.findall(r"(?<!\\)(?:\\\\)*\{(?:[^{}]|(?R))*\}", output, re.DOTALL)

        # Validate each JSON
        valid_jsons = []
        for json_candidate in json_candidates:
            if self.is_valid_json(json_candidate):
                valid_jsons.append(json_candidate)
                continue

            if self._repair:
                logger.warning(f"Found invalid JSON: {json_candidate}. Trying to repair it...")

                repaired_json = self.repair_json(json_candidate)
                if not self.is_valid_json(repaired_json):
                    logger.warning(f"Could not repair JSON: {repaired_json}. Skipping...")
                    continue

                valid_jsons.append(repaired_json)
                output = output.replace(json_candidate, repaired_json)

        # Check if there are enough valid JSONs
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
