import logging
from typing import List, Optional

import spacy
from presidio_analyzer import AnalyzerEngine

from llm_guard.input_scanners.anonymize import (
    all_entity_types,
    get_recognizers,
    get_regex_patterns,
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

        if not entity_types:
            log.debug(f"No entity types provided, using default: {all_entity_types}")
            entity_types = all_entity_types
        spacy.load("en_core_web_lg")
        self._entity_types = entity_types
        self._analyzer = AnalyzerEngine(
            registry=get_recognizers(get_regex_patterns(regex_pattern_groups_path), [])
        )

    def scan(self, prompt: str, output: str) -> (str, bool):
        if output.strip() == "":
            return prompt, True

        analyzer_results = self._analyzer.analyze(
            text=output,
            language="en",
            entities=self._entity_types,
        )

        if len(analyzer_results) == 0:
            log.debug(f"No sensitive data found in the output")
            return output, True

        log.warning(f"Found sensitive data in the output {analyzer_results}")

        return output, False
