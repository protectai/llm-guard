"""Input scanners init"""

# Lightweight scanners that don't require ML dependencies
from .ban_substrings import BanSubstrings
from .invisible_text import InvisibleText
from .regex import Regex
from .secrets import Secrets

# Keep the util function
from .util import get_scanner_by_name


def get_scanner_class(name: str):
    """
    Lazy import scanners to avoid loading heavy dependencies.

    This function dynamically imports scanner classes only when needed,
    preventing torch/transformers from being loaded unnecessarily.
    """
    lightweight_scanners = {
        "BanSubstrings": BanSubstrings,
        "InvisibleText": InvisibleText,
        "Regex": Regex,
        "Secrets": Secrets,
    }

    if name in lightweight_scanners:
        return lightweight_scanners[name]

    # Heavy scanners with ML dependencies - lazy load
    if name == "Anonymize":
        from .anonymize import Anonymize

        return Anonymize
    elif name == "BanCode":
        from .ban_code import BanCode

        return BanCode
    elif name == "BanCompetitors":
        from .ban_competitors import BanCompetitors

        return BanCompetitors
    elif name == "BanTopics":
        from .ban_topics import BanTopics

        return BanTopics
    elif name == "Code":
        from .code import Code

        return Code
    elif name == "Gibberish":
        from .gibberish import Gibberish

        return Gibberish
    elif name == "Language":
        from .language import Language

        return Language
    elif name == "PromptInjection":
        from .prompt_injection import PromptInjection

        return PromptInjection
    elif name == "Sentiment":
        from .sentiment import Sentiment

        return Sentiment
    elif name == "TokenLimit":
        from .token_limit import TokenLimit

        return TokenLimit
    elif name == "Toxicity":
        from .toxicity import Toxicity

        return Toxicity
    else:
        raise ValueError(f"Unknown scanner: {name}")


# For backward compatibility, expose lightweight scanners directly
__all__ = [
    "BanSubstrings",
    "InvisibleText",
    "Regex",
    "Secrets",
    "get_scanner_by_name",
    "get_scanner_class",
]
