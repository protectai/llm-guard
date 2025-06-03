from __future__ import annotations

from .base import Scanner


def get_scanner_by_name(scanner_name: str, scanner_config: dict | None = None) -> Scanner:
    """
    Returns a scanner by name using lazy imports.

    Parameters:
        scanner_name (str): The name of the scanner.
        scanner_config (Optional[Dict], optional): The configuration for the scanner. Defaults to None.

    Raises:
        ValueError: If the scanner name is unknown.
    """
    if scanner_config is None:
        scanner_config = {}

    # Lightweight scanners with lazy imports
    if scanner_name == "BanSubstrings":
        from .ban_substrings import BanSubstrings

        return BanSubstrings(**scanner_config)

    if scanner_name == "InvisibleText":
        from .invisible_text import InvisibleText

        return InvisibleText()

    if scanner_name == "Regex":
        from .regex import Regex

        return Regex(**scanner_config)

    if scanner_name == "Secrets":
        from .secrets import Secrets

        return Secrets(**scanner_config)

    # Heavy scanners with ML dependencies - lazy import when needed
    if scanner_name == "Anonymize":
        from .anonymize import Anonymize

        return Anonymize(**scanner_config)

    if scanner_name == "BanCode":
        from .ban_code import BanCode

        return BanCode(**scanner_config)

    if scanner_name == "BanCompetitors":
        from .ban_competitors import BanCompetitors

        return BanCompetitors(**scanner_config)

    if scanner_name == "BanTopics":
        from .ban_topics import BanTopics

        return BanTopics(**scanner_config)

    if scanner_name == "Code":
        from .code import Code

        return Code(**scanner_config)

    if scanner_name == "Gibberish":
        from .gibberish import Gibberish

        return Gibberish(**scanner_config)

    if scanner_name == "Language":
        from .language import Language

        return Language(**scanner_config)

    if scanner_name == "PromptInjection":
        from .prompt_injection import PromptInjection

        return PromptInjection(**scanner_config)

    if scanner_name == "Sentiment":
        from .sentiment import Sentiment

        return Sentiment(**scanner_config)

    if scanner_name == "TokenLimit":
        from .token_limit import TokenLimit

        return TokenLimit(**scanner_config)

    if scanner_name == "Toxicity":
        from .toxicity import Toxicity

        return Toxicity(**scanner_config)

    raise ValueError(f"Unknown scanner name: {scanner_name}")
