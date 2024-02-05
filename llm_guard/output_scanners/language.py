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
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (Sequence[str]): A list of valid language codes.
            threshold (float): Minimum confidence score.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """

        self._scanner = InputLanguage(
            valid_languages,
            threshold=threshold,
            match_type=match_type,
            use_onnx=use_onnx,
            transformers_kwargs=transformers_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
