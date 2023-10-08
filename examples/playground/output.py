import logging
from typing import Dict, List

import streamlit as st
from streamlit_tags import st_tags

from llm_guard.input_scanners.anonymize import default_entity_types
from llm_guard.output_scanners import (
    BanSubstrings,
    BanTopics,
    Bias,
    Code,
    Deanonymize,
    Language,
    MaliciousURLs,
    NoRefusal,
    Refutation,
    Regex,
    Relevance,
    Sensitive,
)
from llm_guard.output_scanners.sentiment import Sentiment
from llm_guard.output_scanners.toxicity import Toxicity
from llm_guard.vault import Vault

logger = logging.getLogger("llm-guard-playground")


def init_settings() -> (List, Dict):
    all_scanners = [
        "BanSubstrings",
        "BanTopics",
        "Bias",
        "Code",
        "Deanonymize",
        "Language",
        "MaliciousURLs",
        "NoRefusal",
        "Refutation",
        "Regex",
        "Relevance",
        "Sensitive",
        "Sentiment",
        "Toxicity",
    ]

    st_enabled_scanners = st.sidebar.multiselect(
        "Select scanners",
        options=all_scanners,
        default=all_scanners,
        help="The list can be found here: https://laiyer-ai.github.io/llm-guard/output_scanners/bias/",
    )

    settings = {}

    if "BanSubstrings" in st_enabled_scanners:
        st_bs_expander = st.sidebar.expander(
            "Ban Substrings",
            expanded=False,
        )

        with st_bs_expander:
            st_bs_substrings = st.text_area(
                "Enter substrings to ban (one per line)",
                value="test\nhello\nworld\n",
                height=200,
            ).split("\n")

            st_bs_match_type = st.selectbox("Match type", ["str", "word"])
            st_bs_case_sensitive = st.checkbox("Case sensitive", value=False)
            st_bs_redact = st.checkbox("Redact", value=False)
            st_bs_contains_all = st.checkbox("Contains all", value=False)

        settings["BanSubstrings"] = {
            "substrings": st_bs_substrings,
            "match_type": st_bs_match_type,
            "case_sensitive": st_bs_case_sensitive,
            "redact": st_bs_redact,
            "contains_all": st_bs_contains_all,
        }

    if "BanTopics" in st_enabled_scanners:
        st_bt_expander = st.sidebar.expander(
            "Ban Topics",
            expanded=False,
        )

        with st_bt_expander:
            st_bt_topics = st_tags(
                label="List of topics",
                text="Type and press enter",
                value=["politics", "religion", "money", "crime"],
                suggestions=[],
                maxtags=30,
                key="bt_topics",
            )

            st_bt_threshold = st.slider(
                label="Threshold",
                value=0.75,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="ban_topics_threshold",
            )

        settings["BanTopics"] = {"topics": st_bt_topics, "threshold": st_bt_threshold}

    if "Bias" in st_enabled_scanners:
        st_bias_expander = st.sidebar.expander(
            "Bias",
            expanded=False,
        )

        with st_bias_expander:
            st_bias_threshold = st.slider(
                label="Threshold",
                value=0.75,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="bias_threshold",
            )

        settings["Bias"] = {"threshold": st_bias_threshold}

    if "Code" in st_enabled_scanners:
        st_cd_expander = st.sidebar.expander(
            "Code",
            expanded=False,
        )

        with st_cd_expander:
            st_cd_languages = st.multiselect(
                "Programming languages",
                options=["python", "java", "javascript", "go", "php", "ruby"],
                default=["python"],
            )

            st_cd_mode = st.selectbox("Mode", ["allowed", "denied"], index=0)

        settings["Code"] = {"languages": st_cd_languages, "mode": st_cd_mode}

    if "Language" in st_enabled_scanners:
        st_lan_expander = st.sidebar.expander(
            "Language",
            expanded=False,
        )

        with st_lan_expander:
            st_lan_valid_language = st.multiselect(
                "Languages",
                [
                    "af",
                    "ar",
                    "bg",
                    "bn",
                    "ca",
                    "cs",
                    "cy",
                    "da",
                    "de",
                    "el",
                    "en",
                    "es",
                    "et",
                    "fa",
                    "fi",
                    "fr",
                    "gu",
                    "he",
                    "hi",
                    "hr",
                    "hu",
                    "id",
                    "it",
                    "ja",
                    "kn",
                    "ko",
                    "lt",
                    "lv",
                    "mk",
                    "ml",
                    "mr",
                    "ne",
                    "nl",
                    "no",
                    "pa",
                    "pl",
                    "pt",
                    "ro",
                    "ru",
                    "sk",
                    "sl",
                    "so",
                    "sq",
                    "sv",
                    "sw",
                    "ta",
                    "te",
                    "th",
                    "tl",
                    "tr",
                    "uk",
                    "ur",
                    "vi",
                    "zh-cn",
                    "zh-tw",
                ],
                default=["en"],
            )

        settings["Language"] = {
            "valid_languages": st_lan_valid_language,
        }

    if "MaliciousURLs" in st_enabled_scanners:
        st_murls_expander = st.sidebar.expander(
            "Malicious URLs",
            expanded=False,
        )

        with st_murls_expander:
            st_murls_threshold = st.slider(
                label="Threshold",
                value=0.75,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="murls_threshold",
            )

        settings["MaliciousURLs"] = {"threshold": st_murls_threshold}

    if "NoRefusal" in st_enabled_scanners:
        st_no_ref_expander = st.sidebar.expander(
            "No refusal",
            expanded=False,
        )

        with st_no_ref_expander:
            st_no_ref_threshold = st.slider(
                label="Threshold",
                value=0.5,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="no_ref_threshold",
            )

        settings["NoRefusal"] = {"threshold": st_no_ref_threshold}

    if "Refutation" in st_enabled_scanners:
        st_refu_expander = st.sidebar.expander(
            "Refutation",
            expanded=False,
        )

        with st_refu_expander:
            st_refu_threshold = st.slider(
                label="Threshold",
                value=0.5,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="refu_threshold",
            )

        settings["Refutation"] = {"threshold": st_refu_threshold}

    if "Regex" in st_enabled_scanners:
        st_regex_expander = st.sidebar.expander(
            "Regex",
            expanded=False,
        )

        with st_regex_expander:
            st_regex_patterns = st.text_area(
                "Enter patterns to ban (one per line)",
                value="Bearer [A-Za-z0-9-._~+/]+",
                height=200,
            ).split("\n")

            st_regex_type = st.selectbox(
                "Match type",
                ["good", "bad"],
                index=1,
                help="good: allow only good patterns, bad: ban bad patterns",
            )

            st_redact = st.checkbox(
                "Redact", value=False, help="Replace the matched bad patterns with [REDACTED]"
            )

        settings["Regex"] = {
            "patterns": st_regex_patterns,
            "type": st_regex_type,
            "redact": st_redact,
        }

    if "Relevance" in st_enabled_scanners:
        st_rele_expander = st.sidebar.expander(
            "Relevance",
            expanded=False,
        )

        with st_rele_expander:
            st_rele_threshold = st.slider(
                label="Threshold",
                value=0.5,
                min_value=-1.0,
                max_value=1.0,
                step=0.05,
                key="rele_threshold",
                help="The minimum cosine similarity (-1 to 1) between the prompt and output for the output to be considered relevant.",
            )

        settings["Relevance"] = {"threshold": st_rele_threshold}

    if "Sensitive" in st_enabled_scanners:
        st_sens_expander = st.sidebar.expander(
            "Sensitive",
            expanded=False,
        )

        with st_sens_expander:
            st_sens_entity_types = st_tags(
                label="Sensitive entities",
                text="Type and press enter",
                value=default_entity_types,
                suggestions=default_entity_types
                + ["DATE_TIME", "NRP", "LOCATION", "MEDICAL_LICENSE", "US_PASSPORT"],
                maxtags=30,
                key="sensitive_entity_types",
            )
            st.caption(
                "Check all supported entities: https://microsoft.github.io/presidio/supported_entities/#list-of-supported-entities"
            )

        settings["Sensitive"] = {"entity_types": st_sens_entity_types}

    if "Sentiment" in st_enabled_scanners:
        st_sent_expander = st.sidebar.expander(
            "Sentiment",
            expanded=False,
        )

        with st_sent_expander:
            st_sent_threshold = st.slider(
                label="Threshold",
                value=-0.1,
                min_value=-1.0,
                max_value=1.0,
                step=0.1,
                key="sentiment_threshold",
                help="Negative values are negative sentiment, positive values are positive sentiment",
            )

        settings["Sentiment"] = {"threshold": st_sent_threshold}

    if "Toxicity" in st_enabled_scanners:
        st_tox_expander = st.sidebar.expander(
            "Toxicity",
            expanded=False,
        )

        with st_tox_expander:
            st_tox_threshold = st.slider(
                label="Threshold",
                value=0.0,
                min_value=-1.0,
                max_value=1.0,
                step=0.05,
                key="toxicity_threshold",
                help="A negative value (closer to 0 as the label output) indicates toxicity in the text, while a positive logit (closer to 1 as the label output) suggests non-toxicity.",
            )

        settings["Toxicity"] = {"threshold": st_tox_threshold}

    return st_enabled_scanners, settings


def get_scanner(scanner_name: str, vault: Vault, settings: Dict):
    logger.debug(f"Initializing {scanner_name} scanner")

    if scanner_name == "BanSubstrings":
        return BanSubstrings(
            substrings=settings["substrings"],
            match_type=settings["match_type"],
            case_sensitive=settings["case_sensitive"],
            redact=settings["redact"],
            contains_all=settings["contains_all"],
        )

    if scanner_name == "BanTopics":
        return BanTopics(topics=settings["topics"], threshold=settings["threshold"])

    if scanner_name == "Bias":
        return Bias(threshold=settings["threshold"])

    if scanner_name == "Deanonymize":
        return Deanonymize(vault=vault)

    if scanner_name == "Language":
        return Language(valid_languages=settings["valid_languages"])

    if scanner_name == "Code":
        mode = settings["mode"]

        allowed_languages = None
        denied_languages = None
        if mode == "allowed":
            allowed_languages = settings["languages"]
        elif mode == "denied":
            denied_languages = settings["languages"]

        return Code(allowed=allowed_languages, denied=denied_languages)

    if scanner_name == "MaliciousURLs":
        return MaliciousURLs(threshold=settings["threshold"])

    if scanner_name == "NoRefusal":
        return NoRefusal(threshold=settings["threshold"])

    if scanner_name == "Refutation":
        return Refutation(threshold=settings["threshold"])

    if scanner_name == "Regex":
        match_type = settings["type"]

        good_patterns = None
        bad_patterns = None
        if match_type == "good":
            good_patterns = settings["patterns"]
        elif match_type == "bad":
            bad_patterns = settings["patterns"]

        return Regex(
            good_patterns=good_patterns, bad_patterns=bad_patterns, redact=settings["redact"]
        )

    if scanner_name == "Relevance":
        return Relevance(threshold=settings["threshold"])

    if scanner_name == "Sensitive":
        return Sensitive(entity_types=settings["entity_types"])

    if scanner_name == "Sentiment":
        return Sentiment(threshold=settings["threshold"])

    if scanner_name == "Toxicity":
        return Toxicity(threshold=settings["threshold"])

    raise ValueError("Unknown scanner name")


def scan(
    vault: Vault,
    enabled_scanners: List[str],
    settings: Dict,
    prompt: str,
    text: str,
    fail_fast: bool = False,
) -> (str, Dict[str, bool], Dict[str, float]):
    sanitized_output = text
    results_valid = {}
    results_score = {}

    status_text = "Scanning prompt..."
    if fail_fast:
        status_text = "Scanning prompt (fail fast mode)..."

    with st.status(status_text, expanded=True) as status:
        for scanner_name in enabled_scanners:
            st.write(f"{scanner_name} scanner...")
            scanner = get_scanner(
                scanner_name, vault, settings[scanner_name] if scanner_name in settings else {}
            )
            sanitized_output, is_valid, risk_score = scanner.scan(prompt, sanitized_output)
            results_valid[scanner_name] = is_valid
            results_score[scanner_name] = risk_score

            if fail_fast and not is_valid:
                break

        status.update(label="Scanning complete", state="complete", expanded=False)

    return sanitized_output, results_valid, results_score
