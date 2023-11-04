from typing import List, Optional

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
        allowed: Optional[List[str]] = None,
        denied: Optional[List[str]] = None,
        threshold: float = 0.5,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the Code class.

        Parameters:
            allowed (Optional[List[str]]): A list of programming languages that are allowed in the model output.
            denied (Optional[List[str]]): A list of programming languages that are not allowed in the model output.
            threshold (float): The threshold for the model output to be considered valid. Default is 0.5.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If both 'allowed' and 'denied' lists are provided or if both are empty.
        """

        self._scanner = InputCode(allowed, denied, threshold, use_onnx)

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
