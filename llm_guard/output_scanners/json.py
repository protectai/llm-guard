import json
import re

import regex

from llm_guard.util import get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()
JSON_PATTERN = r"(?<!\\)(?:\\\\)*\{(?:[^{}]|(?R))*\}"


class JSON(Scanner):
    """
    A scanner class to detect, validate and repair JSON structures within a given output.

    It primarily serves to detect JSON objects and arrays using regular expressions,
    then to validate them to ensure their correctness and finally to repair them if necessary.
    """

    def __init__(self, *, required_elements: int = 0, repair: bool = True) -> None:
        """Initialize the JSON scanner.

        Parameters:
            required_elements (int, optional): The minimum number of JSON elements
            that should be present. Defaults to 0.
            repair (bool, optional): Whether to repair the broken JSON. Defaults to False.
        """
        self._required_elements = required_elements
        self._repair = repair
        self._pattern = regex.compile(JSON_PATTERN, re.DOTALL)

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """Check if the input string is a valid JSON.

        Parameters:
            json_str (str): The input string to check.

        Returns:
            bool: True if the input string is a valid JSON, False otherwise.
        """
        try:
            json.loads(json_str)
            return True
        except ValueError as e:
            LOGGER.warning("Invalid JSON", error=e)
            return False

    @staticmethod
    def repair_json(json_str: str) -> str:
        """Repair a broken JSON string.

        Parameters:
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

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, 0.0

        # Find JSON object and array candidates using regular expressions
        json_candidates = self._pattern.findall(output)

        # Validate each JSON
        valid_jsons = []
        for json_candidate in json_candidates:
            if self.is_valid_json(json_candidate):
                valid_jsons.append(json_candidate)
                continue

            if self._repair:
                LOGGER.warning(
                    "Found invalid JSON. Trying to repair it...", json_candidate=json_candidate
                )

                repaired_json = self.repair_json(json_candidate)
                if not self.is_valid_json(repaired_json):
                    LOGGER.warning(
                        "Could not repair JSON. Skipping...", repaired_json=repaired_json
                    )

                    continue

                valid_jsons.append(repaired_json)
                output = output.replace(json_candidate, repaired_json)

        # Check if there are enough valid JSONs
        if len(valid_jsons) < self._required_elements:
            LOGGER.warning(
                "Not all required JSON elements are found",
                num_required_elements=self._required_elements,
                num_found=len(valid_jsons),
            )
            return output, False, 1.0

        # Compare
        if len(valid_jsons) != len(json_candidates):
            LOGGER.warning(
                "Only some JSONs are valid",
                num_valid=len(valid_jsons),
                num_total=len(json_candidates),
            )

            return output, False, 1.0

        return output, True, 0.0
