from typing import Protocol


class Scanner(Protocol):
    """
    An interface for text scanners.

    This protocol defines the contract for classes that scan text outputs from a language model.
    """

    def scan(self, prompt: str, output: str) -> (str, bool):
        """
        Analyzes output of the model and returns sanitized output with a flag indicating if it is valid or malicious.

        Parameters:
            prompt (str): The input prompt.
            output (str): The text output from the language model.

        Returns:
            tuple: A tuple containing the scanned and potentially sanitized text output, and a boolean flag indicating
                   if the output is considered malicious (False) or not (True).
        """
