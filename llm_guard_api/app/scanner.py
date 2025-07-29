import asyncio
import time
from typing import Dict, List, Optional

import structlog
import torch
from opentelemetry import metrics

from llm_guard import input_scanners, output_scanners
from llm_guard.input_scanners.anonymize_helpers import DEBERTA_AI4PRIVACY_v2_CONF
from llm_guard.input_scanners.ban_code import MODEL_SM as BAN_CODE_MODEL
from llm_guard.input_scanners.ban_competitors import MODEL_V1 as BAN_COMPETITORS_MODEL
from llm_guard.input_scanners.ban_topics import MODEL_DEBERTA_BASE_V2 as BAN_TOPICS_MODEL
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

torch.set_num_threads(1)

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


def _configure_model(model: Model, scanner_config: Optional[Dict]):
    if scanner_config is None:
        scanner_config = {}

    if "model_path" in scanner_config and scanner_config["model_path"] is not None:
        model.path = scanner_config["model_path"]
        model.onnx_path = scanner_config["model_path"]
        model.onnx_subfolder = ""
        model.kwargs = {"local_files_only": True}
        scanner_config.pop("model_path")

    if "model_batch_size" in scanner_config:
        model.pipeline_kwargs["batch_size"] = scanner_config["model_batch_size"]
        scanner_config.pop("model_batch_size")

    if "model_max_length" in scanner_config and scanner_config["model_max_length"] > 0:
        model.pipeline_kwargs["max_length"] = scanner_config["model_max_length"]
        scanner_config.pop("model_max_length")

    if (
        "model_onnx_file_name" in scanner_config
        and scanner_config["model_onnx_file_name"] is not None
    ):
        model.onnx_filename = scanner_config["model_onnx_file_name"]
        scanner_config.pop("model_onnx_file_name")


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
        "EmotionDetection",
        "Gibberish",
        "Language",
        "PromptInjection",
        "Toxicity",
    ]:
        scanner_config["use_onnx"] = True

    if scanner_name == "Anonymize":
        _configure_model(DEBERTA_AI4PRIVACY_v2_CONF["DEFAULT_MODEL"], scanner_config)
        scanner_config["recognizer_conf"] = DEBERTA_AI4PRIVACY_v2_CONF

    if scanner_name == "BanCode":
        _configure_model(BAN_CODE_MODEL, scanner_config)
        scanner_config["model"] = BAN_CODE_MODEL

    if scanner_name == "BanTopics":
        _configure_model(BAN_TOPICS_MODEL, scanner_config)
        scanner_config["model"] = BAN_TOPICS_MODEL

    if scanner_name == "BanCompetitors":
        _configure_model(BAN_COMPETITORS_MODEL, scanner_config)
        scanner_config["model"] = BAN_COMPETITORS_MODEL

    if scanner_name == "Code":
        _configure_model(CODE_MODEL, scanner_config)
        scanner_config["model"] = CODE_MODEL

    if scanner_name == "Gibberish":
        _configure_model(GIBBERISH_MODEL, scanner_config)
        scanner_config["model"] = GIBBERISH_MODEL

    if scanner_name == "Language":
        _configure_model(LANGUAGE_MODEL, scanner_config)
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "PromptInjection":
        _configure_model(PROMPT_INJECTION_MODEL, scanner_config)
        scanner_config["model"] = PROMPT_INJECTION_MODEL

    if scanner_name == "Toxicity":
        _configure_model(TOXICITY_MODEL, scanner_config)
        scanner_config["model"] = TOXICITY_MODEL

    if scanner_name == "EmotionDetection":
        from llm_guard.input_scanners.emotion_detection import (
            DEFAULT_MODEL as EMOTION_DETECTION_MODEL,
        )

        _configure_model(EMOTION_DETECTION_MODEL, scanner_config)
        scanner_config["model"] = EMOTION_DETECTION_MODEL

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
        "EmotionDetection",
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
        _configure_model(BAN_CODE_MODEL, scanner_config)
        scanner_config["model"] = BAN_CODE_MODEL

    if scanner_name == "BanCompetitors":
        _configure_model(BAN_COMPETITORS_MODEL, scanner_config)
        scanner_config["model"] = BAN_COMPETITORS_MODEL

    if scanner_name == "BanTopics" or scanner_name == "FactualConsistency":
        _configure_model(BAN_TOPICS_MODEL, scanner_config)
        scanner_config["model"] = BAN_TOPICS_MODEL

    if scanner_name == "Bias":
        _configure_model(BIAS_MODEL, scanner_config)
        scanner_config["model"] = BIAS_MODEL

    if scanner_name == "Code":
        _configure_model(CODE_MODEL, scanner_config)
        scanner_config["model"] = CODE_MODEL

    if scanner_name == "Language":
        _configure_model(LANGUAGE_MODEL, scanner_config)
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "LanguageSame":
        _configure_model(LANGUAGE_MODEL, scanner_config)
        scanner_config["model"] = LANGUAGE_MODEL

    if scanner_name == "MaliciousURLs":
        _configure_model(MALICIOUS_URLS_MODEL, scanner_config)
        scanner_config["model"] = MALICIOUS_URLS_MODEL

    if scanner_name == "NoRefusal":
        _configure_model(NO_REFUSAL_MODEL, scanner_config)
        scanner_config["model"] = NO_REFUSAL_MODEL

    if scanner_name == "Gibberish":
        _configure_model(GIBBERISH_MODEL, scanner_config)
        scanner_config["model"] = GIBBERISH_MODEL

    if scanner_name == "Relevance":
        _configure_model(RELEVANCE_MODEL, scanner_config)
        scanner_config["model"] = RELEVANCE_MODEL

    if scanner_name == "Sensitive":
        _configure_model(DEBERTA_AI4PRIVACY_v2_CONF["DEFAULT_MODEL"], scanner_config)
        scanner_config["recognizer_conf"] = DEBERTA_AI4PRIVACY_v2_CONF

    if scanner_name == "Toxicity":
        _configure_model(TOXICITY_MODEL, scanner_config)
        scanner_config["model"] = TOXICITY_MODEL

    if scanner_name == "EmotionDetection":
        from llm_guard.input_scanners.emotion_detection import (
            DEFAULT_MODEL as EMOTION_DETECTION_MODEL,
        )

        _configure_model(EMOTION_DETECTION_MODEL, scanner_config)
        scanner_config["model"] = EMOTION_DETECTION_MODEL

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
        elapsed_time_seconds=round(elapsed_time_scanner, 2),
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
