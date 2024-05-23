from __future__ import annotations

from llm_guard.input_scanners.toxicity import MatchType, Toxicity as InputToxicity
from llm_guard.model import Model

from .base import Scanner


class Toxicity(Scanner):
    """
    A class used to detect toxicity in the output of a language model.

    This class uses a pre-trained toxicity model from HuggingFace to calculate a toxicity score for the output.
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
        Initializes an instance of the Toxicity class.

        Parameters:
            model: The path to the model. Defaults to None.
            threshold: The threshold used to determine toxicity. Defaults to 0.7.
            match_type: Whether to match the full text or individual sentences. Defaults to MatchType.FULL.
            use_onnx: Whether to use ONNX for inference. Defaults to False.
        """

        self._scanner = InputToxicity(
            model=model,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
