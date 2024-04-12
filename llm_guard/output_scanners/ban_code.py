from typing import Optional

from llm_guard.input_scanners.ban_code import BanCode as InputBanCode
from llm_guard.model import Model

from .base import Scanner


class BanCode(Scanner):
    """
    A scanner that detects code snippets in the model output and blocks them.
    """

    def __init__(
        self,
        *,
        model: Optional[Model] = None,
        threshold: float = 0.9,
        use_onnx: bool = False,
    ):
        """
        Initialize a new BanCode scanner.

        Parameters:
            model (Model, optional): The model to use for scanning.
            threshold (float): The threshold for the model output to consider a code snippet.
            use_onnx (bool): Whether to use the ONNX model for scanning.
        """

        self._scanner = InputBanCode(
            model=model,
            threshold=threshold,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
