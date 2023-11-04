from typing import List, Optional

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
        all_languages: Optional[List[str]] = None,
        low_accuracy_mode: bool = False,
        threshold: float = 0.7,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes.
            all_languages (Optional[List[str]]): All languages to load for detection. Default is all spoken languages.
            low_accuracy_mode (bool): High detection accuracy comes at the cost of being noticeably slower than other language detectors.
            threshold (float): Minimum confidence score
        """

        self._scanner = InputLanguage(
            valid_languages=valid_languages,
            all_languages=all_languages,
            low_accuracy_mode=low_accuracy_mode,
            threshold=threshold,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
