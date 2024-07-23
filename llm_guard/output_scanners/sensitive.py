from __future__ import annotations

from presidio_anonymizer import AnonymizerEngine

from llm_guard.input_scanners.anonymize import (
    ALL_SUPPORTED_LANGUAGES,
    DEFAULT_ENTITY_TYPES,
    Anonymize,
)
from llm_guard.input_scanners.anonymize_helpers import (
    DEBERTA_AI4PRIVACY_v2_CONF,
    get_analyzer,
    get_regex_patterns,
    get_transformers_recognizer,
)
from llm_guard.input_scanners.anonymize_helpers.ner_mapping import NERConfig
from llm_guard.util import calculate_risk_score, get_logger

from ..input_scanners.anonymize_helpers.regex_patterns import (
    DefaultRegexPatterns,
    RegexPatternsReuse,
)
from .base import Scanner

LOGGER = get_logger()


class Sensitive(Scanner):
    """
    A class used to detect sensitive (PII) data in the output of a language model.

    This class uses the Presidio Analyzer Engine and predefined internally patterns (patterns.py) to analyze the output for specified entity types.
    If no entity types are specified, it defaults to checking for all entity types.
    """

    def __init__(
        self,
        *,
        entity_types: list[str] | None = None,
        regex_patterns: list[DefaultRegexPatterns | RegexPatternsReuse] | None = None,
        redact: bool = False,
        recognizer_conf: NERConfig | None = None,
        threshold: float = 0.5,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes an instance of the Sensitive class.

        Parameters:
           entity_types (Optional[Sequence[str]]): The entity types to look for in the output. Defaults to all
                                               entity types.
           regex_patterns (Optional[List[Dict]]): List of regex patterns to use for detection. Default is None.
           redact (bool): Redact found sensitive entities. Default to False.
           recognizer_conf (Optional[Dict]): Configuration to recognize PII data. Default is Ai4Privacy DeBERTa.
           threshold (float): Acceptance threshold. Default is 0.
           use_onnx (bool): Use ONNX model for inference. Default is False.
        """
        if not entity_types:
            LOGGER.debug(
                "No entity types provided, using default", default_entity_types=DEFAULT_ENTITY_TYPES
            )
            entity_types = DEFAULT_ENTITY_TYPES.copy()
        entity_types.append("CUSTOM")

        self._entity_types = entity_types
        self._redact = redact
        self._threshold = threshold

        if not recognizer_conf:
            recognizer_conf = DEBERTA_AI4PRIVACY_v2_CONF

        transformers_recognizer = get_transformers_recognizer(
            recognizer_conf=recognizer_conf,
            use_onnx=use_onnx,
        )
        self._analyzer = get_analyzer(
            transformers_recognizer, get_regex_patterns(regex_patterns), [], ALL_SUPPORTED_LANGUAGES
        )
        self._anonymizer = AnonymizerEngine()

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return prompt, True, 0.0

        analyzer_results = self._analyzer.analyze(
            text=Anonymize.remove_single_quotes(output),
            language="en",
            entities=self._entity_types,
            score_threshold=self._threshold,
        )

        if analyzer_results:
            if self._redact:
                LOGGER.debug("Redacting sensitive entities")
                result = self._anonymizer.anonymize(text=output, analyzer_results=analyzer_results)  # type: ignore
                output = result.text

            risk_score = round(
                max(analyzer_result.score for analyzer_result in analyzer_results), 2
            )
            LOGGER.warning("Found sensitive data in the output", results=analyzer_results)
            return output, False, calculate_risk_score(risk_score, self._threshold)

        LOGGER.debug("No sensitive data found in the output")
        return output, True, 0.0
