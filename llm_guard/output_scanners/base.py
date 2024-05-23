import abc
from typing import Protocol


class Scanner(Protocol):
    """
    An interface for text scanners.

    This protocol defines the contract for classes that scan text outputs from a language model.
    """

    @abc.abstractmethod
    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        """
        Analyzes output of the model and returns sanitized output with a flag indicating if it is valid or malicious.

        Parameters:
            prompt: The input prompt.
            output: The text output from the language model.

        Returns:
            str: The sanitized and processed output as per the scanner's implementation.
            bool: A flag indicating whether the output is valid or not.
            float: Risk score where 0 means no risk and 1 means high risk.
        """
