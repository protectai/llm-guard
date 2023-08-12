import logging
import os
from typing import List, Optional

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine

from llm_guard.input_scanners.anonymize import (
    Anonymize,
    default_entity_types,
    sensitive_patterns_path,
)

from .base import Scanner

log = logging.getLogger(__name__)


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
    ):
        """
        Initializes an instance of the Sensitive class.

        Parameters:
           entity_types (Optional[List[str]]): The entity types to look for in the output. Defaults to all
                                               entity types.
           regex_pattern_groups_path (str): Path to the regex patterns file. Default is sensitive_patterns.json.
        """
        os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disables huggingface/tokenizers warning

        if not entity_types:
            log.debug(f"No entity types provided, using default: {default_entity_types}")
            entity_types = default_entity_types
        entity_types.append("CUSTOM")

        self._entity_types = entity_types
        self._analyzer = AnalyzerEngine(
            registry=Anonymize.get_recognizers(
                Anonymize.get_regex_patterns(regex_pattern_groups_path), []
            ),
            nlp_engine=SpacyNlpEngine({"en": "en_core_web_trf"}),
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return prompt, True, 0.0

        analyzer_results = []
        text_chunks = Anonymize.get_text_chunks(output)
        for text_chunk_index, text in enumerate(text_chunks):
            chunk_results = self._analyzer.analyze(
                text=Anonymize.remove_single_quotes(text),
                language="en",
                entities=self._entity_types,
            )
            analyzer_results.extend(chunk_results)

        if analyzer_results:
            risk_score = max(analyzer_result.score for analyzer_result in analyzer_results)
            log.warning(f"Found sensitive data in the output {analyzer_results}")
            return output, False, risk_score

        log.debug(f"No sensitive data found in the output")
        return output, True, 0.0
