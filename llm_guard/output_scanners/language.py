from typing import Dict, Optional, Sequence, Union

from llm_guard.input_scanners.language import Language as InputLanguage
from llm_guard.input_scanners.language import MatchType

from .base import Scanner


class Language(Scanner):
    """
    Language scanner is responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(
        self,
        valid_languages: Sequence[str],
        *,
        model_path: Optional[str] = None,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            model_path (str): The model path to use for inference.
            valid_languages (Sequence[str]): A list of valid language codes.
            threshold (float): Minimum confidence score.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            model_kwargs (Dict): Keyword arguments passed to the model.
            pipeline_kwargs (Dict): Keyword arguments passed to the pipeline.
        """

        self._scanner = InputLanguage(
            valid_languages,
            model_path=model_path,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
            model_kwargs=model_kwargs,
            pipeline_kwargs=pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
