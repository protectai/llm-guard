from typing import List

from llm_guard.input_scanners.language import Language as InputLanguage

from .base import Scanner


class Language(Scanner):
    """
    Language scanner is responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(
        self,
        valid_languages: List[str],
        threshold: float = 0.7,
        use_onnx: bool = False,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes.
            threshold (float): Minimum confidence score.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
        """

        self._scanner = InputLanguage(
            valid_languages=valid_languages,
            threshold=threshold,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
