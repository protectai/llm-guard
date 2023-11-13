import logging
import os
from typing import Dict, List, Optional

import yaml

from llm_guard import input_scanners, output_scanners
from llm_guard.vault import Vault

logger = logging.getLogger(__name__)


def get_env_config() -> Dict:
    return {
        "debug": os.environ.get(
            "DEBUG", False
        ),  # If true, will enable debug logging. Default is false.
        "scan_fail_fast": os.environ.get(
            "SCAN_FAIL_FAST", False
        ),  # If true, will stop scanning after the first scanner fails. Default is false.
        "scan_prompt_timeout": os.environ.get(
            "SCAN_PROMPT_TIMEOUT", 10
        ),  # Time in seconds after which a prompt scan will timeout. Default is 10 seconds.
        "scan_output_timeout": os.environ.get(
            "SCAN_OUTPUT_TIMEOUT", 30
        ),  # Time in seconds after which an output scan will timeout. Default is 30 seconds.
        "cache_ttl": os.environ.get(
            "CACHE_TTL", 60 * 60
        ),  # Time in seconds after which a cached item expires. Default is 1 hour.
        "cache_max_size": os.environ.get(
            "CACHE_MAX_SIZE", None
        ),  # Maximum number of items to store in the cache. Default is unlimited
        "use_onnx": os.environ.get(
            "USE_ONNX", True
        ),  # If true, will load ONNX models. Default is true.
    }


def load_scanners_from_config(config: Dict, vault: Vault, file_name: str) -> (List, List):
    logger.debug(f"Loading config file: {file_name}")

    with open(file_name, "r") as stream:
        try:
            scanner_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(f"Error loading scanner config file: {exc}")
            return [], []

    logger.debug(f"Loaded scanner config: {scanner_config}")

    # Loading input scanners
    result_input_scanners = []
    for scanner_name in scanner_config["input_scanners"]:
        logger.debug(f"Loading input scanner: {scanner_name}")
        result_input_scanners.append(
            get_input_scanner(
                scanner_name, config, vault, scanner_config["input_scanners"][scanner_name]
            )
        )

    result_output_scanners = []
    for scanner_name in scanner_config["output_scanners"]:
        logger.debug(f"Loading output scanner: {scanner_name}")
        result_output_scanners.append(
            get_output_scanner(
                scanner_name, config, vault, scanner_config["output_scanners"][scanner_name]
            )
        )

    return result_input_scanners, result_output_scanners


def get_input_scanner(
    scanner_name: str, config: Dict, vault: Vault, scanner_config: Optional[Dict] = None
):
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "Anonymize":
        return input_scanners.Anonymize(vault=vault, use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "BanSubstrings":
        return input_scanners.BanSubstrings(**scanner_config)

    if scanner_name == "BanTopics":
        return input_scanners.BanTopics(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Code":
        return input_scanners.Code(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Language":
        return input_scanners.Language(**scanner_config)

    if scanner_name == "PromptInjection":
        return input_scanners.PromptInjection(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Regex":
        return input_scanners.Regex(**scanner_config)

    if scanner_name == "Secrets":
        return input_scanners.Secrets(**scanner_config)

    if scanner_name == "Sentiment":
        return input_scanners.Sentiment(**scanner_config)

    if scanner_name == "TokenLimit":
        return input_scanners.TokenLimit(**scanner_config)

    if scanner_name == "Toxicity":
        return input_scanners.Toxicity(use_onnx=config["use_onnx"], **scanner_config)

    raise ValueError("Unknown scanner name")


def get_output_scanner(
    scanner_name: str, config: Dict, vault: Vault, scanner_config: Optional[Dict] = None
):
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "BanSubstrings":
        return output_scanners.BanSubstrings(**scanner_config)

    if scanner_name == "BanTopics":
        return output_scanners.BanTopics(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Bias":
        return output_scanners.Bias(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Deanonymize":
        return output_scanners.Deanonymize(vault=vault)

    if scanner_name == "FactualConsistency":
        return output_scanners.FactualConsistency(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "JSON":
        return output_scanners.JSON(**scanner_config)

    if scanner_name == "Language":
        return output_scanners.Language(**scanner_config)

    if scanner_name == "LanguageSame":
        return output_scanners.LanguageSame(**scanner_config)

    if scanner_name == "Code":
        return output_scanners.Code(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "MaliciousURLs":
        return output_scanners.MaliciousURLs(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "NoRefusal":
        return output_scanners.NoRefusal(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Regex":
        return output_scanners.Regex(**scanner_config)

    if scanner_name == "Relevance":
        return output_scanners.Relevance(**scanner_config)

    if scanner_name == "Sensitive":
        return output_scanners.Sensitive(use_onnx=config["use_onnx"], **scanner_config)

    if scanner_name == "Sentiment":
        return output_scanners.Sentiment(**scanner_config)

    if scanner_name == "Toxicity":
        return output_scanners.Toxicity(use_onnx=config["use_onnx"], **scanner_config)

    raise ValueError("Unknown scanner name")
