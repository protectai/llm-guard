from typing import List

from llm_guard.input_scanners.language import Language as InputLanguage

from .base import Scanner


class Language(Scanner):
    """
    Language scanner is responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(self, valid_languages: List[str]):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes.
        """

        self._scanner = InputLanguage(valid_languages=valid_languages)

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
