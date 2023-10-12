from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngine, NlpEngineProvider

from .spacy_recognizer import CustomSpacyRecognizer

RECOGNIZER_SPACY_EN_TRF = "en_core_web_trf"
RECOGNIZER_SPACY_EN_PII_DISTILBERT = "en_spacy_pii_distilbert"
RECOGNIZER_SPACY_EN_PII_FAST = "en_spacy_pii_fast"

allowed_recognizers = [
    RECOGNIZER_SPACY_EN_TRF,
    RECOGNIZER_SPACY_EN_PII_DISTILBERT,
    RECOGNIZER_SPACY_EN_PII_FAST,
]


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


def _get_nlp_engine(recognizer: str) -> NlpEngine:
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": recognizer}],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    return provider.create_engine()


def get(recognizer: str, regex_groups, custom_names) -> AnalyzerEngine:
    nlp_engine = _get_nlp_engine(recognizer)

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)
    registry = _add_recognizers(registry, regex_groups, custom_names)
    if recognizer != RECOGNIZER_SPACY_EN_TRF:
        spacy_recognizer = CustomSpacyRecognizer()
        registry.add_recognizer(spacy_recognizer)
        registry.remove_recognizer("SpacyRecognizer")

    return AnalyzerEngine(nlp_engine=nlp_engine, registry=registry, supported_languages=["en"])
