import asyncio
import time
from typing import Dict, List, Optional

import structlog
from opentelemetry import metrics

from llm_guard import input_scanners, output_scanners
from llm_guard.input_scanners.base import Scanner as InputScanner
from llm_guard.output_scanners.base import Scanner as OutputScanner
from llm_guard.vault import Vault

from .config import ScannerConfig
from .util import get_resource_utilization

LOGGER = structlog.getLogger(__name__)

meter = metrics.get_meter_provider().get_meter(__name__)
scanners_valid_counter = meter.create_counter(
    name="scanners.valid",
    unit="1",
    description="measures the number of valid scanners",
)


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
        "BanCode",
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
        "BanCode",
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


class PromptIsInvalid(Exception):
    def __init__(self, scanner_name: str, prompt: str, risk_score: float):
        self.scanner_name = scanner_name
        self.prompt = prompt
        self.risk_score = risk_score

    def __str__(self):
        return f"Prompt is invalid based on {self.scanner_name}: {self.prompt} (risk score: {self.risk_score})"


def scan_prompt(scanner: InputScanner, prompt: str) -> (str, float):
    start_time_scanner = time.time()
    sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
    elapsed_time_scanner = time.time() - start_time_scanner

    scanner_name = type(scanner).__name__
    LOGGER.debug(
        "Scanner completed",
        scanner=scanner_name,
        is_valid=is_valid,
        elapsed_time_seconds=round(elapsed_time_scanner, 6),
    )

    scanners_valid_counter.add(1, {"source": "input", "valid": is_valid, "scanner": scanner_name})

    if not is_valid:
        raise PromptIsInvalid(scanner_name, prompt, risk_score)

    return type(scanner).__name__, risk_score


async def ascan_prompt(scanner: InputScanner, prompt: str) -> (str, float):
    return await asyncio.to_thread(scan_prompt, scanner, prompt)
