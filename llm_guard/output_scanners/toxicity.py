from typing import Dict, Optional, Union

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
        model_path: Optional[str] = None,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the Toxicity class.

        Parameters:
            model_path (str, optional): The path to the model. Defaults to None.
            threshold (float): The threshold used to determine toxicity. Defaults to 0.7.
            match_type (MatchType): Whether to match the full text or individual sentences. Defaults to MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.
            model_kwargs (Optional[Dict]): Optional keyword arguments for the model.
            pipeline_kwargs (Optional[Dict]): Optional keyword arguments for the pipeline.
        """

        self._scanner = InputToxicity(
            model_path=model_path,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
            model_kwargs=model_kwargs,
            pipeline_kwargs=pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
