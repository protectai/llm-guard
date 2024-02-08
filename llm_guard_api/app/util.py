import logging
import sys
from os import getpid
from typing import Dict, Literal

import psutil
import structlog

from llm_guard.util import configure_logger as configure_llm_guard_logger

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

    configure_llm_guard_logger(log_level)


def get_resource_utilization() -> Dict:
    """
    Returns the current resource utilization of the system.

    Returns:
        A dictionary containing the current resource utilization of the system.
    """

    process = psutil.Process(getpid())
    # A float representing the current system-wide CPU utilization as a percentage
    cpu_percent = process.cpu_percent()
    # A float representing process memory utilization as a percentage
    memory_percent = process.memory_percent()
    # Total physical memory
    total_memory_bytes = psutil.virtual_memory().total

    return {
        "cpu_utilization_percent": cpu_percent,
        "memory_utilization_percent": memory_percent,
        "total_memory_available_bytes": total_memory_bytes,
    }
