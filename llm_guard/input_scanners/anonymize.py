import json
import logging
import os
import re
from typing import List, Optional

from faker import Faker
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder
from presidio_anonymizer.entities import PIIEntity, RecognizerResult

from llm_guard.vault import Vault

from .base import Scanner

log = logging.getLogger(__name__)
fake = Faker(seed=100)

sensitive_patterns_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "resources",
    "sensisitive_patterns.json",
)
default_entity_types = [
    "CREDIT_CARD",
    "CRYPTO",
    "EMAIL_ADDRESS",
    "IBAN_CODE",
    "IP_ADDRESS",
    "PERSON",
    "PHONE_NUMBER",
    "US_SSN",
    "US_BANK_NUMBER",
    "CREDIT_CARD_RE",
    "UUID",
]
_entity_faker_map = {
    "CREDIT_CARD": fake.credit_card_number,
    "EMAIL_ADDRESS": fake.email,
    "IBAN_CODE": fake.iban,
    "IP_ADDRESS": fake.ipv4,
    "PERSON": fake.name,
    "PHONE_NUMBER": fake.phone_number,
    "URL": fake.url,
    "US_SSN": fake.ssn,
    "CREDIT_CARD_RE": fake.credit_card_number,
    "UUID": fake.uuid4,
}

DEFAULT_LENGTH = 512  # spaCy's transformer model gives a warning if the length of the string is greater than 512.


class Anonymize(Scanner):
    """
    Anonymize sensitive data in the text using NLP (English only) and predefined regex patterns.

    Anonymizes detected entities with placeholders like [REDACTED_PERSON_1] and stores the real values in a Vault.
    Deanonymizer can be used to replace the placeholders back to their original values.
    """

    def __init__(
        self,
        vault: Vault,
        hidden_names: Optional[List[str]] = None,
        allowed_names: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        preamble: str = "",
        regex_pattern_groups_path: str = sensitive_patterns_path,
        use_faker: bool = False,
    ):
        """
        Initialize an instance of Anonymize class.

        Args:
            vault (Vault): A vault instance to store the anonymized data.
            hidden_names (Optional[List[str]]): List of names to be anonymized e.g. [REDACTED_CUSTOM_1].
            allowed_names (Optional[List[str]]): List of names allowed in the text without anonymizing.
            entity_types (Optional[List[str]]): List of entity types to be detected. If not provided, defaults to all.
            preamble (str): Text to prepend to sanitized prompt. If not provided, defaults to an empty string.
            regex_pattern_groups_path (str): Path to a JSON file with regex pattern groups. If not provided, defaults to sensisitive_patterns.json.
            use_faker (bool): Whether to use faker instead of placeholders in applicable cases. If not provided, defaults to False, replaces with placeholders [REDACTED_PERSON_1].
        """

        os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Disables huggingface/tokenizers warning

        if not entity_types:
            log.debug(f"No entity types provided, using default: {default_entity_types}")
            entity_types = default_entity_types
        entity_types.append("CUSTOM")

        if not hidden_names:
            hidden_names = []

        self._vault = vault
        self._entity_types = entity_types
        self._allowed_names = allowed_names
        self._preamble = preamble
        self._use_faker = use_faker
        self._analyzer = AnalyzerEngine(
            registry=Anonymize.get_recognizers(
                Anonymize.get_regex_patterns(regex_pattern_groups_path), hidden_names
            ),
            nlp_engine=SpacyNlpEngine({"en": "en_core_web_trf"}),
        )

    @staticmethod
    def get_regex_patterns(json_path: str) -> List[dict]:
        """
        Load regex patterns from a specified JSON file.

        Args:
            json_path (str): Path to the JSON file containing regex patterns.

        Returns:
            List[dict]: List of regex patterns with each dictionary containing "name", "expressions", "context", and "score".
                        Returns an empty list if file not found or parsing error occurred.
        """
        regex_groups = []
        try:
            with open(json_path, "r") as myfile:
                pattern_groups_raw = json.load(myfile)
            for group in pattern_groups_raw:
                regex_groups.append(
                    {
                        "name": group["name"].upper(),
                        "expressions": group["expressions"],
                        "context": group["context"],
                        "score": group["score"],
                    }
                )
                log.debug(f"Loaded regex pattern for {group['name']}")
        except FileNotFoundError:
            log.warning(f"Could not find {json_path}")
        except json.decoder.JSONDecodeError as json_error:
            log.warning(f"Could not parse {json_path}: {json_error}")
        return regex_groups

    @staticmethod
    def get_recognizers(regex_groups, custom_names) -> RecognizerRegistry:
        """
        Create a RecognizerRegistry and populate it with regex patterns and custom names.

        Args:
            regex_groups: List of regex patterns.
            custom_names: List of custom names to recognize.

        Returns:
            RecognizerRegistry: A RecognizerRegistry object loaded with regex and custom name recognizers.
        """
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        if len(custom_names) > 0:
            registry.add_recognizer(
                PatternRecognizer(supported_entity="CUSTOM", deny_list=custom_names)
            )

        for pattern_data in regex_groups:
            label = pattern_data["name"]
            compiled_patterns = pattern_data["expressions"]
            patterns = []
            for pattern in compiled_patterns:
                patterns.append(Pattern(name=label, regex=pattern, score=pattern_data["score"]))
            registry.add_recognizer(
                PatternRecognizer(
                    supported_entity=label,
                    patterns=patterns,
                    context=pattern_data["context"],
                )
            )

        return registry

    @staticmethod
    def _remove_conflicts_and_get_text_manipulation_data(
        analyzer_results: List[RecognizerResult],
    ) -> List[RecognizerResult]:
        """
        Remove conflicting and redundant detections from the analyzer results.
        """
        tmp_analyzer_results = []
        # This list contains all elements which we need to check a single result
        # against. If a result is dropped, it can also be dropped from this list
        # since it is intersecting with another result, and we selected the other one.
        other_elements = analyzer_results.copy()
        for result in analyzer_results:
            other_elements.remove(result)

            is_merge_same_entity_type = False
            for other_element in other_elements:
                if other_element.entity_type != result.entity_type:
                    continue
                if result.intersects(other_element) == 0:
                    continue

                other_element.start = min(result.start, other_element.start)
                other_element.end = max(result.end, other_element.end)
                other_element.score = max(result.score, other_element.score)
                is_merge_same_entity_type = True
                break
            if not is_merge_same_entity_type:
                other_elements.append(result)
                tmp_analyzer_results.append(result)
            else:
                log.debug(f"removing element {result} from " f"results list due to merge")

        unique_text_metadata_elements = []
        # This list contains all elements which we need to check a single result
        # against. If a result is dropped, it can also be dropped from this list
        # since it is intersecting with another result, and we selected the other one.
        other_elements = tmp_analyzer_results.copy()
        for result in tmp_analyzer_results:
            other_elements.remove(result)
            result_conflicted = Anonymize.__is_result_conflicted_with_other_elements(
                other_elements, result
            )
            if not result_conflicted:
                other_elements.append(result)
                unique_text_metadata_elements.append(result)
            else:
                log.debug(f"removing element {result} from results list due to conflict")
        return unique_text_metadata_elements

    @staticmethod
    def __is_result_conflicted_with_other_elements(other_elements, result):
        """
        Check if the given result conflicts with any other elements.
        """
        return any([result.has_conflict(other_element) for other_element in other_elements])

    @staticmethod
    def _merge_entities_with_whitespace_between(
        text: str, analyzer_results: List[RecognizerResult]
    ) -> List[RecognizerResult]:
        """
        Merge adjacent entities of the same type separated by whitespace.
        """
        merged_results = []
        prev_result = None
        for result in analyzer_results:
            if prev_result is not None:
                if prev_result.entity_type == result.entity_type:
                    if re.search(r"^( )+$", text[prev_result.end : result.start]):
                        merged_results.remove(prev_result)
                        result.start = prev_result.start
            merged_results.append(result)
            prev_result = result
        return merged_results

    @staticmethod
    def _get_entity_placeholder(entity_type: str, index: int, use_faker: bool) -> str:
        result = f"[REDACTED_{entity_type}_{index}]"
        if use_faker and entity_type in _entity_faker_map:
            result = _entity_faker_map[entity_type]()
        return result

    @staticmethod
    def _anonymize(
        prompt: str, pii_entities: List[PIIEntity], use_faker: bool
    ) -> (str, List[tuple]):
        """
        Replace detected entities in the prompt with anonymized placeholders.

        Args:
            prompt (str): Original text prompt.
            pii_entities (List[PIIEntity]): List of entities detected in the prompt.
            use_faker (bool): Whether to use faker to generate fake data.

        Returns:
            str: Sanitized text.
            List[tuple]: List of tuples representing the replaced entities and their corresponding placeholders.
        """
        text_replace_builder = TextReplaceBuilder(original_text=prompt)

        entity_type_counter = {}
        for pii_entity in pii_entities:
            entity_type = pii_entity.entity_type
            entity_value = text_replace_builder.get_text_in_position(
                pii_entity.start, pii_entity.end
            )

            if entity_type not in entity_type_counter:
                entity_type_counter[entity_type] = {}

            if entity_value not in entity_type_counter[entity_type]:
                entity_type_counter[entity_type][entity_value] = (
                    len(entity_type_counter[entity_type]) + 1
                )

        results = []
        sorted_pii_entities = sorted(pii_entities, reverse=True)
        for pii_entity in sorted_pii_entities:
            entity_type = pii_entity.entity_type
            entity_value = text_replace_builder.get_text_in_position(
                pii_entity.start, pii_entity.end
            )

            index = entity_type_counter[entity_type][entity_value]
            changed_entity = Anonymize._get_entity_placeholder(entity_type, index, use_faker)

            results.append((changed_entity, prompt[pii_entity.start : pii_entity.end]))

            text_replace_builder.replace_text_get_insertion_index(
                changed_entity, pii_entity.start, pii_entity.end
            )

        return text_replace_builder.output_text, results

    @staticmethod
    def remove_single_quotes(text: str) -> str:
        text_without_single_quotes = text.replace("'", " ")
        return text_without_single_quotes

    @staticmethod
    def get_text_chunks(full_text: str) -> List[str]:
        if len(full_text) > DEFAULT_LENGTH:
            text_chunks = [
                full_text[t - DEFAULT_LENGTH : t]
                for t in range(
                    DEFAULT_LENGTH,
                    len(full_text) + DEFAULT_LENGTH,
                    DEFAULT_LENGTH,
                )
            ]
        else:
            text_chunks = [full_text]

        return text_chunks

    def scan(self, prompt: str) -> (str, bool, float):
        risk_score = 0.0
        if prompt.strip() == "":
            return prompt, True, risk_score

        analyzer_results = []
        text_chunks = Anonymize.get_text_chunks(prompt)
        for text_chunk_index, text in enumerate(text_chunks):
            chunk_results = self._analyzer.analyze(
                text=Anonymize.remove_single_quotes(text),
                language="en",
                entities=self._entity_types,
                allow_list=self._allowed_names,
            )
            analyzer_results.extend(chunk_results)

        risk_score = (
            max(analyzer_result.score for analyzer_result in analyzer_results)
            if analyzer_results
            else 0.0
        )
        analyzer_results = self._remove_conflicts_and_get_text_manipulation_data(analyzer_results)
        merged_results = self._merge_entities_with_whitespace_between(prompt, analyzer_results)

        sanitized_prompt, anonymized_results = self._anonymize(
            prompt, merged_results, self._use_faker
        )

        if prompt != sanitized_prompt:
            log.warning(
                f"Found sensitive data in the prompt and replaced it: {merged_results}, risk score: {risk_score}"
            )
            self._vault.extend(anonymized_results)
            return self._preamble + sanitized_prompt, False, risk_score

        log.debug(f"Prompt does not have sensitive data to replace. Risk score is {risk_score}")

        return prompt, True, 0.0
