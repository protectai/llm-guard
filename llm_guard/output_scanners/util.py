from typing import Dict, Optional

from .base import Scanner


def get_scanner_by_name(scanner_name: str, scanner_config: Optional[Dict] = None) -> Scanner:
    """
    Get scanner by name using lazy imports.

    Parameters:
        scanner_name (str): Name of scanner.
        scanner_config (Optional[Dict], optional): Scanner configuration. Defaults to None.

    Raises:
        ValueError: If scanner name is unknown.
    """
    if scanner_config is None:
        scanner_config = {}

    # Lightweight scanners with lazy imports
    if scanner_name == "BanSubstrings":
        from .ban_substrings import BanSubstrings

        return BanSubstrings(**scanner_config)

    if scanner_name == "ReadingTime":
        from .reading_time import ReadingTime

        return ReadingTime(**scanner_config)

    if scanner_name == "Regex":
        from .regex import Regex

        return Regex(**scanner_config)

    # Heavy scanners with ML dependencies - lazy import when needed
    if scanner_name == "BanCode":
        from .ban_code import BanCode

        return BanCode(**scanner_config)

    if scanner_name == "BanCompetitors":
        from .ban_competitors import BanCompetitors

        return BanCompetitors(**scanner_config)

    if scanner_name == "BanTopics":
        from .ban_topics import BanTopics

        return BanTopics(**scanner_config)

    if scanner_name == "Bias":
        from .bias import Bias

        return Bias(**scanner_config)

    if scanner_name == "Deanonymize":
        from .deanonymize import Deanonymize

        return Deanonymize(**scanner_config)

    if scanner_name == "FactualConsistency":
        from .factual_consistency import FactualConsistency

        return FactualConsistency(**scanner_config)

    if scanner_name == "Gibberish":
        from .gibberish import Gibberish

        return Gibberish(**scanner_config)

    if scanner_name == "JSON":
        from .json import JSON

        return JSON(**scanner_config)

    if scanner_name == "Language":
        from .language import Language

        return Language(**scanner_config)

    if scanner_name == "LanguageSame":
        from .language_same import LanguageSame

        return LanguageSame(**scanner_config)

    if scanner_name == "Code":
        from .code import Code

        return Code(**scanner_config)

    if scanner_name == "MaliciousURLs":
        from .malicious_urls import MaliciousURLs

        return MaliciousURLs(**scanner_config)

    if scanner_name == "NoRefusal":
        from .no_refusal import NoRefusal

        return NoRefusal(**scanner_config)

    if scanner_name == "NoRefusalLight":
        from .no_refusal import NoRefusalLight

        return NoRefusalLight()

    if scanner_name == "Relevance":
        from .relevance import Relevance

        return Relevance(**scanner_config)

    if scanner_name == "Sensitive":
        from .sensitive import Sensitive

        return Sensitive(**scanner_config)

    if scanner_name == "Sentiment":
        from .sentiment import Sentiment

        return Sentiment(**scanner_config)

    if scanner_name == "Toxicity":
        from .toxicity import Toxicity

        return Toxicity(**scanner_config)

    if scanner_name == "URLReachability":
        from .url_reachabitlity import URLReachability

        return URLReachability(**scanner_config)

    raise ValueError(f"Unknown scanner name: {scanner_name}!")
