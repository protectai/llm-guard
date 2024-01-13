from typing import Sequence

from llm_guard.input_scanners.code import Code as InputCode

from .base import Scanner


class Code(Scanner):
    """
    A class for scanning if the model output includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or deny specific programming languages.
    """

    def __init__(
        self,
        languages: Sequence[str],
        *,
        is_blocked: bool = True,
        threshold: float = 0.5,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the Code class.

        Parameters:
            languages (Sequence[str]): The list of programming languages to allow or deny.
            is_blocked (bool): Whether the languages are blocked or allowed. Default is True.
            threshold (float): The threshold for the model output to be considered valid. Default is 0.5.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If both 'allowed' and 'denied' lists are provided or if both are empty.
        """

        self._scanner = InputCode(
            languages, is_blocked=is_blocked, threshold=threshold, use_onnx=use_onnx
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
