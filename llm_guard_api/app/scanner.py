from typing import Dict, List, Optional

import structlog

from llm_guard import input_scanners, output_scanners
from llm_guard.input_scanners.base import Scanner as InputScanner
from llm_guard.output_scanners.base import Scanner as OutputScanner
from llm_guard.vault import Vault

from .config import ScannerConfig
from .util import get_resource_utilization

LOGGER = structlog.getLogger(__name__)


def get_input_scanners(scanners: List[ScannerConfig], vault: Vault) -> List[InputScanner]:
    """
    Load input scanners from the configuration file.
    """

    input_scanners_loaded = []
    for scanner in scanners:
        LOGGER.debug("Loading input scanner", scanner=scanner.type, **get_resource_utilization())
        input_scanners_loaded.append(
            _get_input_scanner(
                scanner.type,
                scanner.params,
                vault=vault,
            )
        )

    return input_scanners_loaded


def get_output_scanners(scanners: List[ScannerConfig], vault: Vault) -> List[OutputScanner]:
    """
    Load output scanners from the configuration file.
    """
    output_scanners_loaded = []
    for scanner in scanners:
        LOGGER.debug("Loading output scanner", scanner=scanner.type, **get_resource_utilization())
        output_scanners_loaded.append(
            _get_output_scanner(
                scanner.type,
                scanner.params,
                vault=vault,
            )
        )

    return output_scanners_loaded


def _get_input_scanner(
    scanner_name: str,
    scanner_config: Optional[Dict],
    *,
    vault: Vault,
):
    if scanner_config is None:
        scanner_config = {}

    if scanner_name == "Anonymize":
        scanner_config["vault"] = vault

    if scanner_name in [
        "Anonymize",
        "BanTopics",
        "Code",
        "Gibberish",
        "Language",
        "PromptInjection",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = True

    return input_scanners.get_scanner_by_name(scanner_name, scanner_config)


def _get_output_scanner(
    scanner_name: str,
    scanner_config: Optional[Dict],
    *,
    vault: Vault,
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
        "Gibberish",
        "Language",
        "LanguageSame",
        "MaliciousURLs",
        "NoRefusal",
        "Relevance",
        "Sensitive",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = True

    return output_scanners.get_scanner_by_name(scanner_name, scanner_config)
