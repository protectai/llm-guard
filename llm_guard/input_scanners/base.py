from typing import Protocol


class Scanner(Protocol):
    """
    Scanner protocol that defines the interface for scanners.

    This is used to ensure that the scanners implement a common interface and can be used interchangeably.
    """

    def scan(self, prompt: str) -> (str, bool, float):
        """
        Process and sanitize the input prompt according to the specific scanner's implementation.

        Args:
            prompt (str): The input prompt that needs to be processed.

        Returns:
            str: The sanitized and processed prompt as per the scanner's implementation.
            bool: A flag indicating whether the prompt is valid or not.
            float: Risk score where 0 means no risk and 1 means high risk.
        """
