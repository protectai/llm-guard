from typing import List

from llm_guard.util import lazy_load_dep, logger

from .base import Scanner


class Language(Scanner):
    """
    A Scanner subclass responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(self, valid_languages: List[str]):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes.
        """

        self._lang_detect = lazy_load_dep("ftlangdetect")
        self._valid_languages = valid_languages

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        try:
            result = self._lang_detect.detect(prompt)
        except self._lang_detect.LangDetectException as e:
            logger.warning(f"Could not detect language: {e}")
            result = {"lang": "", "score": 0.0}

        if result["lang"] in self._valid_languages:
            logger.debug(
                f'Language "{result["lang"]}" is found in the text and valid (score: {result["score"]})'
            )
            return prompt, True, 0.0

        logger.warning(f'Language "{result["lang"]}" is not allowed (score: {result["score"]})')

        return prompt, False, 1.0
