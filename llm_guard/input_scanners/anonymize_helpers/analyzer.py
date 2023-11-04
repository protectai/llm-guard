from typing import Dict, List

import spacy
from presidio_analyzer import (
    AnalyzerEngine,
    EntityRecognizer,
    Pattern,
    PatternRecognizer,
    RecognizerRegistry,
)
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider

from .ner_mapping import ALL_RECOGNIZER_CONF
from .transformers_recognizer import TransformersRecognizer


def _add_recognizers(
    registry: RecognizerRegistry, regex_groups, custom_names
) -> RecognizerRegistry:
    """
    Create a RecognizerRegistry and populate it with regex patterns and custom names.

    Args:
        regex_groups: List of regex patterns.
        custom_names: List of custom names to recognize.

    Returns:
        RecognizerRegistry: A RecognizerRegistry object loaded with regex and custom name recognizers.
    """

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


def _get_nlp_engine() -> NlpEngine:
    # Use small spacy model, for faster inference.
    if not spacy.util.is_package("en_core_web_sm"):
        spacy.cli.download("en_core_web_sm")

    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }

    return NlpEngineProvider(nlp_configuration=configuration).create_engine()


def get_transformers_recognizer(recognizer_conf: Dict, use_onnx: bool = False) -> EntityRecognizer:
    if recognizer_conf not in ALL_RECOGNIZER_CONF:
        raise ValueError("Recognizer configuration is not found")

    model_path = recognizer_conf.get("DEFAULT_MODEL_PATH")
    supported_entities = recognizer_conf.get("PRESIDIO_SUPPORTED_ENTITIES")
    transformers_recognizer = TransformersRecognizer(
        model_path=model_path,
        supported_entities=supported_entities,
    )
    transformers_recognizer.load_transformer(use_onnx=use_onnx, **recognizer_conf)
    return transformers_recognizer


def get_analyzer(
    recognizer: EntityRecognizer, regex_groups, custom_names: List[str]
) -> AnalyzerEngine:
    nlp_engine = _get_nlp_engine()

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)
    registry = _add_recognizers(registry, regex_groups, custom_names)
    registry.add_recognizer(recognizer)
    registry.remove_recognizer("SpacyRecognizer")

    return AnalyzerEngine(nlp_engine=nlp_engine, registry=registry, supported_languages=["en"])
