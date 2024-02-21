from typing import Dict, Optional, Union

from llm_guard.input_scanners.gibberish import Gibberish as InputGibberish
from llm_guard.input_scanners.gibberish import MatchType

from .base import Scanner


class Gibberish(Scanner):
    """
    A scanner that detects gibberish text.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
           transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """

        self._scanner = InputGibberish(
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
            transformers_kwargs=transformers_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
