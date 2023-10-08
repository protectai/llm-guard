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
    }


def load_scanners_from_config(
    vault: Vault, file_name: Optional[str] = "scanners.yml"
) -> (List, List):
    logger.debug(f"Loading config file: {file_name}")

    config = {}
    with open(file_name, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(f"Error loading config file: {exc}")
            return [], []

    logger.debug(f"Loaded config: {config}")

    # Loading input scanners
    result_input_scanners = []
    for scanner_name in config["input_scanners"]:
        logger.debug(f"Loading input scanner: {scanner_name}")
        result_input_scanners.append(
            get_input_scanner(scanner_name, vault, config["input_scanners"][scanner_name])
        )

    result_output_scanners = []
    for scanner_name in config["output_scanners"]:
        logger.debug(f"Loading output scanner: {scanner_name}")
        result_output_scanners.append(
            get_output_scanner(scanner_name, vault, config["output_scanners"][scanner_name])
        )

    return result_input_scanners, result_output_scanners


def get_input_scanner(scanner_name: str, vault: Vault, config: Optional[Dict] = None):
    if config is None:
        config = {}

    if scanner_name == "Anonymize":
        return input_scanners.Anonymize(vault=vault, **config)

    if scanner_name == "BanSubstrings":
        return input_scanners.BanSubstrings(**config)

    if scanner_name == "BanTopics":
        return input_scanners.BanTopics(**config)

    if scanner_name == "Code":
        return input_scanners.Code(**config)

    if scanner_name == "PromptInjection":
        return input_scanners.PromptInjection(**config)

    if scanner_name == "PromptInjectionV2":
        return input_scanners.PromptInjectionV2(**config)

    if scanner_name == "Regex":
        return input_scanners.Regex(**config)

    if scanner_name == "Secrets":
        return input_scanners.Secrets(**config)

    if scanner_name == "Sentiment":
        return input_scanners.Sentiment(**config)

    if scanner_name == "TokenLimit":
        return input_scanners.TokenLimit(**config)

    if scanner_name == "Toxicity":
        return input_scanners.Toxicity(**config)

    raise ValueError("Unknown scanner name")


def get_output_scanner(scanner_name: str, vault: Vault, config: Optional[Dict] = None):
    if config is None:
        config = {}

    if scanner_name == "BanSubstrings":
        return output_scanners.BanSubstrings(**config)

    if scanner_name == "BanTopics":
        return output_scanners.BanTopics(**config)

    if scanner_name == "Bias":
        return output_scanners.Bias(**config)

    if scanner_name == "Deanonymize":
        return output_scanners.Deanonymize(vault=vault)

    if scanner_name == "Code":
        return output_scanners.Code(**config)

    if scanner_name == "MaliciousURLs":
        return output_scanners.MaliciousURLs(**config)

    if scanner_name == "NoRefusal":
        return output_scanners.NoRefusal(**config)

    if scanner_name == "Refutation":
        return output_scanners.Refutation(**config)

    if scanner_name == "Regex":
        return output_scanners.Regex(**config)

    if scanner_name == "Relevance":
        return output_scanners.Relevance(**config)

    if scanner_name == "Sensitive":
        return output_scanners.Sensitive(**config)

    if scanner_name == "Sentiment":
        return output_scanners.Sentiment(**config)

    if scanner_name == "Toxicity":
        return output_scanners.Toxicity(**config)

    raise ValueError("Unknown scanner name")
