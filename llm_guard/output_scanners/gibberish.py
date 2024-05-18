from __future__ import annotations

from llm_guard.input_scanners.gibberish import Gibberish as InputGibberish, MatchType
from llm_guard.model import Model

from .base import Scanner


class Gibberish(Scanner):
    """
    A scanner that detects gibberish text.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold: float = 0.7,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           model (Model, optional): The model used.
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
        """

        self._scanner = InputGibberish(
            model=model,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
