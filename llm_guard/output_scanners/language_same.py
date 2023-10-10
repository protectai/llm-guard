from llm_guard.util import lazy_load_dep, logger

from .base import Scanner


class LanguageSame(Scanner):
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(self):
        """
        Initializes the LanguageSame scanner.
        """
        self._lang_detect = lazy_load_dep("langdetect")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "" or output.strip() == "":
            return prompt, True, 0.0

        try:
            prompt_language = self._lang_detect.detect(prompt)
        except self._lang_detect.LangDetectException as e:
            logger.warning(f"Could not detect prompt language: {e}")
            prompt_language = ""

        try:
            output_language = self._lang_detect.detect(output)
        except self._lang_detect.LangDetectException as e:
            logger.warning(f"Could not detect output language: {e}")
            output_language = ""

        if prompt_language == output_language:
            logger.debug(f"Prompt and output are in the same language: {output_language}")
            return output, True, 0.0

        logger.warning(f"Prompt is in {prompt_language} but output is in {output_language}")

        return output, False, 1.0
