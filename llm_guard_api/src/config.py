import logging
import os
import re
from typing import Any, Dict, Optional

import yaml

from llm_guard import input_scanners, output_scanners
from llm_guard.vault import Vault

logger = logging.getLogger(__name__)

_var_matcher = re.compile(r"\${([^}^{]+)}")
_tag_matcher = re.compile(r"[^$]*\${([^}^{]+)}.*")


def _path_constructor(_loader: Any, node: Any):
    def replace_fn(match):
        envparts = f"{match.group(1)}:".split(":")
        return os.environ.get(envparts[0], envparts[1])

    return _var_matcher.sub(replace_fn, node.value)


def load_yaml(filename: str) -> dict:
    yaml.add_implicit_resolver("!envvar", _tag_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("!envvar", _path_constructor, yaml.SafeLoader)
    try:
        with open(filename, "r") as f:
            return yaml.safe_load(f.read())
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as exc:
        logger.error(f"Error loading YAML file: {exc}")
        return dict()


def get_config(vault: Vault, file_name: str) -> Dict:
    logger.debug(f"Loading config file: {file_name}")

    conf = load_yaml(file_name)
    if conf == {}:
        return {}

    result = {"app": conf["app"], "input_scanners": [], "output_scanners": []}

    # Loading input scanners
    for scanner in conf["input_scanners"]:
        logger.debug(f"Loading input scanner: {scanner['type']}")
        result["input_scanners"].append(
            _get_input_scanner(
                scanner["type"],
                scanner["params"],
                vault=vault,
            )
        )

    # Loading output scanners
    for scanner in conf["output_scanners"]:
        logger.debug(f"Loading output scanner: {scanner['type']}")
        result["output_scanners"].append(
            _get_output_scanner(
                scanner["type"],
                scanner["params"],
                vault=vault,
            )
        )

    return result


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
