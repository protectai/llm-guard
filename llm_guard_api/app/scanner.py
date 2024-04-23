import asyncio
import time
from typing import Dict, List, Optional

import structlog
from opentelemetry import metrics

from llm_guard import input_scanners, output_scanners
from llm_guard.input_scanners.anonymize_helpers import DISTILBERT_AI4PRIVACY_v2_CONF
from llm_guard.input_scanners.ban_code import MODEL_SM as BAN_CODE_MODEL
from llm_guard.input_scanners.ban_competitors import MODEL_SMALL as BAN_COMPETITORS_MODEL
from llm_guard.input_scanners.ban_topics import MODEL_ROBERTA_BASE_C_V2 as BAN_TOPICS_MODEL
from llm_guard.input_scanners.base import Scanner as InputScanner
from llm_guard.input_scanners.code import DEFAULT_MODEL as CODE_MODEL
from llm_guard.input_scanners.gibberish import DEFAULT_MODEL as GIBBERISH_MODEL
from llm_guard.input_scanners.language import DEFAULT_MODEL as LANGUAGE_MODEL
from llm_guard.input_scanners.prompt_injection import V2_MODEL as PROMPT_INJECTION_MODEL
from llm_guard.input_scanners.toxicity import DEFAULT_MODEL as TOXICITY_MODEL
from llm_guard.model import Model
from llm_guard.output_scanners.base import Scanner as OutputScanner
from llm_guard.output_scanners.bias import DEFAULT_MODEL as BIAS_MODEL
from llm_guard.output_scanners.malicious_urls import DEFAULT_MODEL as MALICIOUS_URLS_MODEL
from llm_guard.output_scanners.no_refusal import DEFAULT_MODEL as NO_REFUSAL_MODEL
from llm_guard.output_scanners.relevance import MODEL_EN_BGE_SMALL as RELEVANCE_MODEL
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


def _use_local_model(model: Model, path: Optional[str]):
    if path is None:
        return

    model.path = path
    model.onnx_path = path
    model.onnx_subfolder = ""
    model.kwargs = {"local_files_only": True}


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

    if scanner_name == "Anonymize":
        _use_local_model(DISTILBERT_AI4PRIVACY_v2_CONF, scanner_config.get("model_path"))
        scanner_config["recognizer_conf"] = DISTILBERT_AI4PRIVACY_v2_CONF

    if scanner_name == "BanCode":
        _use_local_model(BAN_CODE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_CODE_MODEL

    if scanner_name == "BanTopics":
        _use_local_model(BAN_TOPICS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_TOPICS_MODEL

    if scanner_name == "BanCompetitors":
        _use_local_model(BAN_COMPETITORS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_COMPETITORS_MODEL

    if scanner_name == "Code":
        _use_local_model(CODE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = CODE_MODEL

    if scanner_name == "Gibberish":
        _use_local_model(GIBBERISH_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = GIBBERISH_MODEL

    if scanner_name == "Language":
        _use_local_model(LANGUAGE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "PromptInjection":
        _use_local_model(PROMPT_INJECTION_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = PROMPT_INJECTION_MODEL

    if scanner_name == "Toxicity":
        _use_local_model(TOXICITY_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = TOXICITY_MODEL

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
        "Language",
        "LanguageSame",
        "MaliciousURLs",
        "NoRefusal",
        "FactualConsistency",
        "Gibberish",
        "Relevance",
        "Sensitive",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = True

    if scanner_name == "BanCode":
        _use_local_model(BAN_CODE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_CODE_MODEL

    if scanner_name == "BanCompetitors":
        _use_local_model(BAN_COMPETITORS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_COMPETITORS_MODEL

    if scanner_name == "BanTopics" or scanner_name == "FactualConsistency":
        _use_local_model(BAN_TOPICS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BAN_TOPICS_MODEL

    if scanner_name == "Bias":
        _use_local_model(BIAS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = BIAS_MODEL

    if scanner_name == "Code":
        _use_local_model(CODE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = CODE_MODEL

    if scanner_name == "Language":
        _use_local_model(LANGUAGE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "LanguageSame":
        _use_local_model(LANGUAGE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "MaliciousURLs":
        _use_local_model(MALICIOUS_URLS_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = MALICIOUS_URLS_MODEL

    if scanner_name == "NoRefusal":
        _use_local_model(NO_REFUSAL_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = NO_REFUSAL_MODEL

    if scanner_name == "Gibberish":
        _use_local_model(GIBBERISH_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = GIBBERISH_MODEL

    if scanner_name == "Relevance":
        _use_local_model(RELEVANCE_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = RELEVANCE_MODEL

    if scanner_name == "Sensitive":
        _use_local_model(DISTILBERT_AI4PRIVACY_v2_CONF, scanner_config.get("model_path"))
        scanner_config["recognizer_conf"] = DISTILBERT_AI4PRIVACY_v2_CONF

    if scanner_name == "Toxicity":
        _use_local_model(TOXICITY_MODEL, scanner_config.get("model_path"))
        scanner_config["model"] = TOXICITY_MODEL

    return output_scanners.get_scanner_by_name(scanner_name, scanner_config)


class InputIsInvalid(Exception):
    def __init__(self, scanner_name: str, input: str, risk_score: float):
        self.scanner_name = scanner_name
        self.input = input
        self.risk_score = risk_score

    def __str__(self):
        return f"Input is invalid based on {self.scanner_name}: {self.input} (risk score: {self.risk_score})"


def scan_prompt(scanner: InputScanner, prompt: str) -> (str, float):
    start_time_scanner = time.time()
    sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
    elapsed_time_scanner = time.time() - start_time_scanner

    scanner_name = type(scanner).__name__
    LOGGER.debug(
        "Input scanner completed",
        scanner=scanner_name,
        is_valid=is_valid,
        elapsed_time_seconds=round(elapsed_time_scanner, 6),
    )

    scanners_valid_counter.add(1, {"source": "input", "valid": is_valid, "scanner": scanner_name})

    if not is_valid:
        raise InputIsInvalid(scanner_name, prompt, risk_score)

    return type(scanner).__name__, risk_score


async def ascan_prompt(scanner: InputScanner, prompt: str) -> (str, float):
    return await asyncio.to_thread(scan_prompt, scanner, prompt)


def scan_output(scanner: OutputScanner, prompt: str, output: str) -> (str, float):
    start_time_scanner = time.time()
    sanitized_output, is_valid, risk_score = scanner.scan(prompt, output)
    elapsed_time_scanner = time.time() - start_time_scanner

    scanner_name = type(scanner).__name__
    LOGGER.debug(
        "Output scanner completed",
        scanner=scanner_name,
        is_valid=is_valid,
        elapsed_time_seconds=round(elapsed_time_scanner, 6),
    )

    scanners_valid_counter.add(1, {"source": "output", "valid": is_valid, "scanner": scanner_name})

    if not is_valid:
        raise InputIsInvalid(scanner_name, output, risk_score)

    return type(scanner).__name__, risk_score


async def ascan_output(scanner: OutputScanner, prompt: str, output: str) -> (str, float):
    return await asyncio.to_thread(scan_output, scanner, prompt, output)
