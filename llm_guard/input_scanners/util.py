from typing import Dict, Optional

from .anonymize import Anonymize
from .ban_substrings import BanSubstrings
from .ban_topics import BanTopics
from .base import Scanner
from .code import Code
from .language import Language
from .prompt_injection import PromptInjection
from .regex import Regex
from .secrets import Secrets
from .sentiment import Sentiment
from .token_limit import TokenLimit
from .toxicity import Toxicity


def get_scanner_by_name(scanner_name: str, scanner_config: Optional[Dict] = None) -> Scanner:
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "Anonymize":
        return Anonymize(**scanner_config)

    if scanner_name == "BanSubstrings":
        return BanSubstrings(**scanner_config)

    if scanner_name == "BanTopics":
        return BanTopics(**scanner_config)

    if scanner_name == "Code":
        return Code(**scanner_config)

    if scanner_name == "Language":
        return Language(**scanner_config)

    if scanner_name == "PromptInjection":
        return PromptInjection(**scanner_config)

    if scanner_name == "Regex":
        return Regex(**scanner_config)

    if scanner_name == "Secrets":
        return Secrets(**scanner_config)

    if scanner_name == "Sentiment":
        return Sentiment(**scanner_config)

    if scanner_name == "TokenLimit":
        return TokenLimit(**scanner_config)

    if scanner_name == "Toxicity":
        return Toxicity(**scanner_config)

    raise ValueError("Unknown scanner name")
