from typing import Dict, Optional

from .ban_substrings import BanSubstrings
from .ban_topics import BanTopics
from .base import Scanner
from .bias import Bias
from .code import Code
from .deanonymize import Deanonymize
from .factual_consistency import FactualConsistency
from .json import JSON
from .language import Language
from .language_same import LanguageSame
from .malicious_urls import MaliciousURLs
from .no_refusal import NoRefusal
from .regex import Regex
from .relevance import Relevance
from .sensitive import Sensitive
from .sentiment import Sentiment
from .toxicity import Toxicity


def get_scanner_by_name(scanner_name: str, scanner_config: Optional[Dict] = None) -> Scanner:
    """
    Get scanner by name.

    Args:
        scanner_name (str): Name of scanner.
        scanner_config (Optional[Dict], optional): Scanner configuration. Defaults to None.

    Raises:
        ValueError: If scanner name is unknown.
    """
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "BanSubstrings":
        return BanSubstrings(**scanner_config)

    if scanner_name == "BanTopics":
        return BanTopics(**scanner_config)

    if scanner_name == "Bias":
        return Bias(**scanner_config)

    if scanner_name == "Deanonymize":
        return Deanonymize(**scanner_config)

    if scanner_name == "FactualConsistency":
        return FactualConsistency(**scanner_config)

    if scanner_name == "JSON":
        return JSON(**scanner_config)

    if scanner_name == "Language":
        return Language(**scanner_config)

    if scanner_name == "LanguageSame":
        return LanguageSame(**scanner_config)

    if scanner_name == "Code":
        return Code(**scanner_config)

    if scanner_name == "MaliciousURLs":
        return MaliciousURLs(**scanner_config)

    if scanner_name == "NoRefusal":
        return NoRefusal(**scanner_config)

    if scanner_name == "Regex":
        return Regex(**scanner_config)

    if scanner_name == "Relevance":
        return Relevance(**scanner_config)

    if scanner_name == "Sensitive":
        return Sensitive(**scanner_config)

    if scanner_name == "Sentiment":
        return Sentiment(**scanner_config)

    if scanner_name == "Toxicity":
        return Toxicity(**scanner_config)

    raise ValueError("Unknown scanner name")
