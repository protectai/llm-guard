from typing import List, Optional

from llm_guard.util import calculate_risk_score, lazy_load_dep, logger

from .base import Scanner

lingua = lazy_load_dep("lingua")


def convert_to_languages(lang_codes: List[str]) -> List[lingua.IsoCode639_1]:
    enum_list = []
    for code in lang_codes:
        try:
            enum_value = lingua.IsoCode639_1[code.upper()]
            enum_list.append(enum_value)
        except KeyError:
            logger.warning(f"Language code {code} not found in IsoCode639_1 enum.")
    return enum_list


class Language(Scanner):
    """
    A Scanner subclass responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(
        self,
        valid_languages: List[str],
        all_languages: Optional[List[str]] = None,
        low_accuracy_mode: bool = False,
        threshold: float = 0.6,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes in ISO 639-1.
            all_languages (Optional[List[str]]): All languages to load for detection. Default is all spoken languages.
            low_accuracy_mode (bool): High detection accuracy comes at the cost of being noticeably slower than other language detectors.
            threshold (float): Minimum confidence score
        """

        detector = lingua.LanguageDetectorBuilder

        if all_languages is None:
            detector = detector.from_all_spoken_languages()
        else:
            detector = detector.from_iso_codes_639_1(*convert_to_languages(all_languages))

        if low_accuracy_mode:
            detector = detector.with_low_accuracy_mode()

        self._detector = detector.with_preloaded_language_models().build()
        self._threshold = threshold
        self._valid_languages = convert_to_languages(valid_languages)

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        detected_languages = self._detector.compute_language_confidence_values(prompt)
        if len(detected_languages) == 0:
            logger.warning(f"None of allowed languages found in the text")

            return prompt, False, 1.0

        for detected_language in detected_languages:
            if (
                detected_language.language.iso_code_639_1 in self._valid_languages
                and detected_language.value >= self._threshold
            ):
                logger.debug(
                    f"Language {detected_language.language} is found in the text; score: {detected_language.value}"
                )
                return prompt, True, 0.0

        logger.warning(f"Confidence is too low for provided languages")

        return prompt, False, calculate_risk_score(detected_languages[0].value, self._threshold)
