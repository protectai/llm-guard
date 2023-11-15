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
        scanner_config["vault"] = vault

    if scanner_name in [
        "Anonymize",
        "BanTopics",
        "Code",
        "Language",
        "PromptInjection",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = config["use_onnx"]

    return input_scanners.get_scanner_by_name(scanner_name, scanner_config)


def get_output_scanner(
    scanner_name: str, config: Dict, vault: Vault, scanner_config: Optional[Dict] = None
):
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "Deanonymize":
        scanner_config["vault"] = vault

    if scanner_name in [
        "BanTopics",
        "Bias",
        "Code",
        "FactualConsistency",
        "Language",
        "LanguageSame",
        "MaliciousURLs",
        "NoRefusal",
        "Relevance",
        "Sensitive",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = config["use_onnx"]

    return output_scanners.get_scanner_by_name(scanner_name, scanner_config)
