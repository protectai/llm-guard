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
        self._lang_detect = lazy_load_dep("ftlangdetect")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "" or output.strip() == "":
            return prompt, True, 0.0

        try:
            prompt_result = self._lang_detect.detect(prompt)
        except self._lang_detect.LangDetectException as e:
            logger.warning(f"Could not detect prompt language: {e}")
            prompt_result = {"lang": "", "score": 0.0}

        try:
            output_result = self._lang_detect.detect(output)
        except self._lang_detect.LangDetectException as e:
            logger.warning(f"Could not detect output language: {e}")
            output_result = {"lang": "", "score": 0.0}

        if prompt_result["lang"] == output_result["lang"]:
            logger.debug(f'Prompt and output are in the same language: {output_result["lang"]}')
            return output, True, 0.0

        logger.warning(
            f'Prompt is in {prompt_result["lang"]} ({prompt_result["score"]}) but output is in {output_result["lang"]} ({output_result["score"]})'
        )

        return output, False, 1.0
