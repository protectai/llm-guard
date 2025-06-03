"""LLM output scanners init"""

# Lightweight scanners that don't require ML dependencies
from .ban_substrings import BanSubstrings
from .regex import Regex
from .reading_time import ReadingTime

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
        "Regex": Regex,
        "ReadingTime": ReadingTime,
    }

    if name in lightweight_scanners:
        return lightweight_scanners[name]

    # Heavy scanners with ML dependencies - lazy load
    if name == "BanCode":
        from .ban_code import BanCode

        return BanCode
    elif name == "BanCompetitors":
        from .ban_competitors import BanCompetitors

        return BanCompetitors
    elif name == "BanTopics":
        from .ban_topics import BanTopics

        return BanTopics
    elif name == "Bias":
        from .bias import Bias

        return Bias
    elif name == "Code":
        from .code import Code

        return Code
    elif name == "Deanonymize":
        from .deanonymize import Deanonymize

        return Deanonymize
    elif name == "FactualConsistency":
        from .factual_consistency import FactualConsistency

        return FactualConsistency
    elif name == "Gibberish":
        from .gibberish import Gibberish

        return Gibberish
    elif name == "JSON":
        from .json import JSON

        return JSON
    elif name == "Language":
        from .language import Language

        return Language
    elif name == "LanguageSame":
        from .language_same import LanguageSame

        return LanguageSame
    elif name == "MaliciousURLs":
        from .malicious_urls import MaliciousURLs

        return MaliciousURLs
    elif name == "NoRefusal":
        from .no_refusal import NoRefusal

        return NoRefusal
    elif name == "NoRefusalLight":
        from .no_refusal import NoRefusalLight

        return NoRefusalLight
    elif name == "Relevance":
        from .relevance import Relevance

        return Relevance
    elif name == "Sensitive":
        from .sensitive import Sensitive

        return Sensitive
    elif name == "Sentiment":
        from .sentiment import Sentiment

        return Sentiment
    elif name == "Toxicity":
        from .toxicity import Toxicity

        return Toxicity
    elif name == "URLReachability":
        from .url_reachabitlity import URLReachability

        return URLReachability
    else:
        raise ValueError(f"Unknown scanner: {name}")


# For backward compatibility, expose lightweight scanners directly
__all__ = [
    "BanSubstrings",
    "Regex",
    "ReadingTime",
    "get_scanner_by_name",
    "get_scanner_class",
]
