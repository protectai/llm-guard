from typing import Union

from llm_guard.input_scanners.toxicity import MatchType
from llm_guard.input_scanners.toxicity import Toxicity as InputToxicity

from .base import Scanner


class Toxicity(Scanner):
    """
    A class used to detect toxicity in the output of a language model.

    This class uses a pre-trained toxicity model from HuggingFace to calculate a toxicity score for the output.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the Toxicity class.

        Parameters:
            threshold (float): The threshold used to determine toxicity. Defaults to 0.7.
            match_type (MatchType): Whether to match the full text or individual sentences. Defaults to MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.
        """

        self._scanner = InputToxicity(threshold=threshold, match_type=match_type, use_onnx=use_onnx)

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
