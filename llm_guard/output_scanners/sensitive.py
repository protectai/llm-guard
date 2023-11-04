from typing import Dict, List, Optional

from presidio_anonymizer import AnonymizerEngine

from llm_guard.input_scanners.anonymize import (
    Anonymize,
    default_entity_types,
    sensitive_patterns_path,
)
from llm_guard.input_scanners.anonymize_helpers import (
    BERT_BASE_NER_CONF,
    get_analyzer,
    get_transformers_recognizer,
)
from llm_guard.util import logger

from .base import Scanner


class Sensitive(Scanner):
    """
    A class used to detect sensitive (PII) data in the output of a language model.

    This class uses the Presidio Analyzer Engine and predefined internally patterns (sensitive_patterns.json) to analyze the output for specified entity types.
    If no entity types are specified, it defaults to checking for all entity types.
    """

    def __init__(
        self,
        entity_types: Optional[List[str]] = None,
        regex_pattern_groups_path: str = sensitive_patterns_path,
        redact: bool = False,
        recognizer_conf: Optional[Dict] = BERT_BASE_NER_CONF,
        threshold: float = 0,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the Sensitive class.

        Parameters:
           entity_types (Optional[List[str]]): The entity types to look for in the output. Defaults to all
                                               entity types.
           regex_pattern_groups_path (str): Path to the regex patterns file. Default is sensitive_patterns.json.
           redact (bool): Redact found sensitive entities. Default to False.
           recognizer_conf (Optional[Dict]): Configuration to recognize PII data. Default is dslim/bert-base-NER.
           threshold (float): Acceptance threshold. Default is 0.
           use_onnx (bool): Use ONNX model for inference. Default is False.
        """
        if not entity_types:
            logger.debug(f"No entity types provided, using default: {default_entity_types}")
            entity_types = default_entity_types.copy()
        entity_types.append("CUSTOM")

        self._entity_types = entity_types
        self._redact = redact
        self._threshold = threshold

        transformers_recognizer = get_transformers_recognizer(recognizer_conf, use_onnx)
        self._analyzer = get_analyzer(
            transformers_recognizer, Anonymize.get_regex_patterns(regex_pattern_groups_path), []
        )
        self._anonymizer = AnonymizerEngine()

    def scan(self, prompt: str, output: str) -> (str, bool, float):
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
                logger.debug(f"Redacting sensitive entities")
                result = self._anonymizer.anonymize(text=output, analyzer_results=analyzer_results)
                output = result.text

            risk_score = max(analyzer_result.score for analyzer_result in analyzer_results)
            logger.warning(f"Found sensitive data in the output {analyzer_results}")
            return output, False, risk_score

        logger.debug(f"No sensitive data found in the output")
        return output, True, 0.0
