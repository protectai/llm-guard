from typing import List, Optional

from llm_guard.input_scanners.language import convert_to_languages
from llm_guard.util import calculate_risk_score, lazy_load_dep, logger

from .base import Scanner


class LanguageSame(Scanner):
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(
        self,
        allowed_languages: Optional[List[str]] = None,
        low_accuracy_mode: bool = False,
        threshold: float = 0.1,
    ):
        """
        Initializes the LanguageSame scanner.

        Parameters:
            allowed_languages (List[str]): A list of valid language codes in ISO 639-1. By default, it will use all languages.
            low_accuracy_mode (bool): High detection accuracy comes at the cost of being noticeably slower than other language detectors.
            threshold (float): Minimum confidence score
        """

        lingua = lazy_load_dep("lingua")
        detector = lingua.LanguageDetectorBuilder

        if allowed_languages is None:
            detector = detector.from_all_spoken_languages()
            logger.debug("No allowed languages provided, using default: all spoken")
        else:
            detector = detector.from_iso_codes_639_1(*convert_to_languages(allowed_languages))

        if low_accuracy_mode:
            detector = detector.with_low_accuracy_mode()

        self._detector = detector.with_preloaded_language_models().build()
        self._threshold = threshold

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "" or output.strip() == "":
            return prompt, True, 0.0

        prompt_languages = self._detector.compute_language_confidence_values(prompt)
        output_languages = self._detector.compute_language_confidence_values(output)

        if len(prompt_languages) == 0:
            logger.warning(f"None of allowed languages found in the prompt")
            return output, False, 1.0

        if len(output_languages) == 0:
            logger.warning(f"None of allowed languages found in the output")
            return output, False, 1.0

        if prompt_languages[0].language != output_languages[0].language:
            logger.debug(
                f"Prompt and output are in the same language; {prompt_languages[0].language} != {output_languages[0].language}"
            )
            return output, False, 1.0

        if prompt_languages[0].value < self._threshold:
            logger.warning(f"Confidence of the prompt language is too low: {prompt_languages}")
            return output, False, calculate_risk_score(prompt_languages[0].value, self._threshold)

        if output_languages[0].value < self._threshold:
            logger.warning(f"Confidence of the output language is too low: {output_languages}")
            return output, False, calculate_risk_score(output_languages[0].value, self._threshold)

        logger.debug(
            f"Language {prompt_languages[0].language} is found both in the prompt and output; input score: {prompt_languages[0].value}, output score: {output_languages[0].value}"
        )
        return output, True, 0.0
