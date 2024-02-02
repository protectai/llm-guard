import importlib
import json
import logging
import re
import sys
from functools import lru_cache
from typing import Any, Dict, List, Literal, Optional

import structlog

LOGGER = structlog.getLogger(__name__)

"""
This file contains utility functions.
This is meant for internal use and not part of the public API.
"""

LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
EXTERNAL_LOGGERS = {
    "transformers",
}


def configure_logger(log_level: LOG_LEVELS = "INFO"):
    """
    Configures the logger for the package.

    Args:
        log_level: The log level to use for the logger. It should be one of the following strings:
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
    """
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())
    for log_name in EXTERNAL_LOGGERS:
        logging.getLogger(log_name).setLevel(logging.WARNING)


def _get_library_name() -> str:
    return __name__.split(".")[0]


def _get_library_root_logger() -> logging.Logger:
    return logging.getLogger(_get_library_name())


def get_logger(name: Optional[str] = None) -> Any:
    """
    Return a logger with the specified name.
    """

    if name is None:
        name = _get_library_name()

    return structlog.getLogger(name)


# Detect pytorch device
@lru_cache(maxsize=None)  # Unbounded cache
def device():
    torch = lazy_load_dep("torch")
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    elif torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def read_json_file(json_path: str) -> Dict[str, List[str]]:
    """
    Reads a JSON file and returns its contents as a Python dictionary.

    Args:
        json_path: The path to the JSON file to be read.

    Returns:
        A dictionary representation of the JSON file's contents. If an error occurs (e.g. file not found or JSON decoding error),
        an empty dictionary is returned and an error message is logged.

    Raises:
        FileNotFoundError: If the provided json_path does not point to an existing file.
        json.decoder.JSONDecodeError: If the provided file cannot be parsed as JSON.
    """

    result = {}
    try:
        with open(json_path, "r") as myfile:
            result = json.load(myfile)
            LOGGER.debug("Loaded json file", path=json_path)
    except FileNotFoundError:
        LOGGER.error("Could not find file", path=json_path)
    except json.decoder.JSONDecodeError as json_error:
        LOGGER.error("Could not parse file", path=json_path, error=json_error)
    return result


def combine_json_results(results: Dict[str, List[str]]) -> List[str]:
    """
    Combines values from a dictionary with list values into a single list.

    Args:
       results: A dictionary where values are lists.

    Returns:
       A list containing all the values from the input dictionary.
    """

    all_items = []
    for item in results:
        all_items.extend(results[item])
    return all_items


def lazy_load_dep(import_name: str, package_name: Optional[str] = None):
    """Helper function to lazily load optional dependencies. If the dependency is not
    present, the function will raise an error _when used_.

    NOTE: This wrapper adds a warning message at import time.
    """

    if package_name is None:
        package_name = import_name

    spec = importlib.util.find_spec(import_name)
    if spec is None:
        LOGGER.warning(
            f"Optional feature dependent on missing package: {import_name} was initialized.\n"
            f"Use `pip install {package_name}` to install the package if running locally."
        )

    return importlib.import_module(import_name)


def calculate_risk_score(score: float, threshold: float) -> float:
    if score > threshold:
        return 1.0

    risk_score = round(abs(score - threshold) / threshold, 1)
    # Ensure risk score is between 0 and 1
    return min(max(risk_score, 0), 1)


def chunk_text(text: str, chunk_size: int) -> List[str]:
    text = text.strip()
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def chunk_text_by_sentences(text: str, max_chunk_size: int) -> List[str]:
    nltk = lazy_load_dep("nltk")

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    sentences = nltk.sent_tokenize(text.strip())

    chunks = []
    chunk = []
    chunk_size = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        if chunk_size + sentence_length <= max_chunk_size:
            chunk.append(sentence)
            chunk_size += sentence_length
        else:
            if chunk:  # Check if chunk is non-empty
                chunks.append(" ".join(chunk))
            chunk = [sentence]
            chunk_size = sentence_length

    if chunk:  # Don't forget the last chunk, and check if it's non-empty
        chunks.append(" ".join(chunk))

    return [chunk for chunk in chunks if chunk.strip()]


def split_text_by_sentences(text: str) -> List[str]:
    nltk = lazy_load_dep("nltk")

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    return nltk.sent_tokenize(text.strip())


url_pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def extract_urls(text: str) -> List[str]:
    """
    Extracts URLs from the given text.
    """
    return url_pattern.findall(text)
