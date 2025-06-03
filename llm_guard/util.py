from __future__ import annotations

import importlib
import logging
import re
import sys
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, TextIO, cast

import structlog

LOGGER = structlog.getLogger(__name__)

if TYPE_CHECKING:
    pass  # torch import moved to device() function

"""
This file contains utility functions.
This is meant for internal use and not part of the public API.
"""

LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
EXTERNAL_LOGGERS = {
    "transformers",
    "presidio-analyzer",
}
CHUNK = NamedTuple("CHUNKS", [("start", int), ("end", int)])


def configure_logger(
    log_level: LOG_LEVELS = "INFO",
    render_json: bool = False,
    stream: TextIO = sys.stdout,
):
    """
    Configures the logger for the package.

    Args:
        log_level: The log level to use for the logger. It should be one of:
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        render_json: Whether to render log messages in JSON format.
        stream: The stream to write log messages to. Default is sys.stdout.
    """
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        stream=stream,
    )

    log_level_to_int = {
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "ERROR": logging.ERROR,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    render_processors = [structlog.dev.ConsoleRenderer()]
    if render_json:
        render_processors = [structlog.processors.JSONRenderer()]

    structlog.configure(
        context_class=dict,
        wrapper_class=structlog.make_filtering_bound_logger(log_level_to_int[log_level]),
        logger_factory=structlog.PrintLoggerFactory(stream),
        cache_logger_on_first_use=False,
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.dict_tracebacks,
        ]
        + render_processors,
    )
    for log_name in EXTERNAL_LOGGERS:
        logging.getLogger(log_name).setLevel(logging.WARNING)


def _get_library_name() -> str:
    return __name__.split(".")[0]


def get_logger(name: str | None = None) -> Any:
    """
    Return a logger with the specified name.
    """

    if name is None:
        name = _get_library_name()

    return structlog.getLogger(name)


# Detect pytorch device
@lru_cache(maxsize=None)  # Unbounded cache
def device():
    try:
        torch = cast("torch", lazy_load_dep("torch"))
        if torch.cuda.is_available():
            return torch.device("cuda:0")
        elif torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    except ImportError:
        # Fallback for ONNX-only installations
        import platform
        import os

        # Simple device detection without torch
        if os.environ.get("CUDA_VISIBLE_DEVICES"):
            return "cuda"
        elif platform.system() == "Darwin":
            return "mps"
        return "cpu"


def lazy_load_dep(import_name: str, package_name: str | None = None):
    """Helper function to lazily load optional dependencies. If the dependency is not
    present, the function will raise an error _when used_.

    NOTE: This wrapper adds a warning message at import time.
    """

    if package_name is None:
        package_name = import_name

    spec = importlib.util.find_spec(import_name)  # type: ignore
    if spec is None:
        LOGGER.warning(
            f"Optional feature dependent on missing package: {import_name} was initialized.\n"
            f"Use `pip install {package_name}` to install the package if running locally."
        )

    return importlib.import_module(import_name)


def calculate_risk_score(score: float, threshold: float) -> float:
    """
    Calculate the risk score based on the threshold. The risk score is a value between -1 and 1.
    Before the threshold, the risk score is negative and after the threshold, the risk score is positive.
    """
    if score > threshold:
        risk_score = round((score - threshold) / (1 - threshold), 1)
    else:
        risk_score = round((score - threshold) / threshold, 1)

    return min(max(risk_score, -1), 1)


def chunk_text(text: str, chunk_size: int) -> list[str]:
    text = text.strip()
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def split_text_by_sentences(text: str) -> list[str]:
    nltk = lazy_load_dep("nltk")

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab")

    return nltk.sent_tokenize(text.strip())


def split_text_to_word_chunks(
    input_length: int, chunk_length: int, overlap_length: int
) -> list[CHUNK]:
    """The function calculates chunks of text with size chunk_length. Each chunk has overlap_length number of
    words to create context and continuity for the model

    :param input_length: Length of input_ids for a given text
    :type input_length: int
    :param chunk_length: Length of each chunk of input_ids.
    Should match the max input length of the transformer model
    :type chunk_length: int
    :param overlap_length: Number of overlapping words in each chunk
    :type overlap_length: int
    :return: List of start and end positions for individual text chunks
    :rtype: list[List]
    """
    if input_length < chunk_length:
        return [CHUNK(0, input_length)]
    if chunk_length <= overlap_length:
        LOGGER.warning(
            "overlap_length should be shorter than chunk_length, setting overlap_length to by half of chunk_length"
        )
        overlap_length = chunk_length // 2
    return [
        CHUNK(i, min([i + chunk_length, input_length]))
        for i in range(0, input_length - overlap_length, chunk_length - overlap_length)
    ]


def truncate_tokens_head_tail(tokens, max_length=512, head_length=128, tail_length=382):
    if len(tokens) > max_length:
        head_tokens = tokens[:head_length]
        tail_tokens = tokens[-tail_length:]
        tokens = head_tokens + tail_tokens
    return tokens


url_pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


def extract_urls(text: str) -> list[str]:
    """
    Extracts URLs from the given text.
    """
    return url_pattern.findall(text)


def remove_markdown(text):
    # Patterns to remove Markdown elements but keep text inside ** and *
    patterns = [
        r"\*\*([^\*]+)\*\*",  # Bold, preserves text inside
        r"\*([^\*]+)\*",  # Italic, preserves text inside
        r"\!\[[^\]]+\]\([^\)]+\)",  # Images
        r"\[[^\]]+\]\([^\)]+\)",  # Links
        r"\#{1,6}\s",  # Headers
        r"\>+",  # Blockquotes
        r"`{1,3}[^`]+`{1,3}",  # Inline code and code blocks
        r"\n{2,}",  # Multiple newlines
    ]

    clean_text = text
    for pattern in patterns:
        # Use substitution to preserve the text inside ** and *
        if "([^\*]+)" in pattern:
            clean_text = re.sub(pattern, r"\1", clean_text)
        else:
            clean_text = re.sub(pattern, "", clean_text)

    # Extra cleanup for simpler elements
    clean_text = re.sub(r"\*|\_|\`", "", clean_text)

    return clean_text.strip()
