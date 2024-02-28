from typing import Dict, Optional, Union

from llm_guard.input_scanners.gibberish import Gibberish as InputGibberish
from llm_guard.input_scanners.gibberish import MatchType, default_model_path

from .base import Scanner


class Gibberish(Scanner):
    """
    A scanner that detects gibberish text.
    """

    def __init__(
        self,
        *,
        model_path: str = default_model_path,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           model_path (str): The path to the model.
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
           model_kwargs (Dict): Keyword arguments passed to the model.
           pipeline_kwargs (Dict): Keyword arguments passed to the pipeline.
        """

        self._scanner = InputGibberish(
            model_path=model_path,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
            model_kwargs=model_kwargs,
            pipeline_kwargs=pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
