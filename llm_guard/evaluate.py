import time
from typing import Dict, Optional

from .input_scanners.base import Scanner as InputScanner
from .output_scanners.base import Scanner as OutputScanner
from .util import logger

"""
This file contains main functionality for scanning both prompts and outputs of Large Language Models (LLMs).
There are two primary functions: 'scan_prompt' and 'scan_output'.
Each function takes a list of scanner objects and applies each scanner to the input string(s).

An Scanner in this context is an object of a class that inherits from either `input_scanners.Scanner` or `output_scanners.Scanner` base classes.
These base classes define an `scan` method that takes in a string and returns a processed string and a boolean value indicating the validity of the input string.

These functions return the processed string after all scanners have been applied, along with a dictionary mapping the name of each scanner to its validity result.
"""


def scan_prompt(
    scanners: list[InputScanner], prompt: str, fail_fast: Optional[bool] = False
) -> (str, Dict[str, bool], Dict[str, float]):
    """
    Scans a given prompt using the provided scanners.

    Args:
        scanners: A list of scanner objects. Each scanner should be an instance of a class that inherits from `Scanner`.
        prompt: The input prompt string to be scanned.
        fail_fast: A boolean value indicating whether to stop scanning after the first scanner fails.

    Returns:
        A tuple containing:
            - The processed prompt string after applying all scanners.
            - A dictionary mapping scanner names to boolean values indicating whether the input prompt is valid according to each scanner.
            - A dictionary mapping scanner names to float values of risk scores, where 0 is no risk, and 1 is high risk.
    """

    sanitized_prompt = prompt
    results_valid = {}
    results_score = {}

    if len(scanners) == 0 or prompt.strip() == "":
        return sanitized_prompt, results_valid, results_score

    start_time = time.time()
    for scanner in scanners:
        start_time_scanner = time.time()
        sanitized_prompt, is_valid, risk_score = scanner.scan(sanitized_prompt)
        elapsed_time_scanner = time.time() - start_time_scanner
        logger.debug(
            f"Scanner {type(scanner).__name__}: Valid={is_valid}. Elapsed time: {elapsed_time_scanner:.6f} seconds"
        )

        results_valid[type(scanner).__name__] = is_valid
        results_score[type(scanner).__name__] = risk_score
        if fail_fast and not is_valid:
            break

    elapsed_time = time.time() - start_time
    logger.info(
        f"Scanned prompt with the score: {results_score}. Elapsed time: {elapsed_time:.6f} seconds"
    )

    return sanitized_prompt, results_valid, results_score


def scan_output(
    scanners: list[OutputScanner], prompt: str, output: str, fail_fast: Optional[bool] = False
) -> (str, Dict[str, bool], Dict[str, float]):
    """
    Scans a given output of a large language model using the provided scanners.

    Args:
        scanners: A list of scanner objects. Each scanner should be an instance of a class that inherits from `Scanner`.
        prompt: The input prompt string that produced the output.
        output: The output string to be scanned.
        fail_fast: A boolean value indicating whether to stop scanning after the first scanner fails.

    Returns:
        A tuple containing:
            - The processed output string after applying all scanners.
            - A dictionary mapping scanner names to boolean values indicating whether the output is valid according to each scanner.
            - A dictionary mapping scanner names to float values of risk scores, where 0 is no risk, and 1 is high risk.
    """

    sanitized_output = output
    results_valid = {}
    results_score = {}

    if len(scanners) == 0 or output.strip() == "":
        return sanitized_output, results_valid, results_score

    start_time = time.time()
    for scanner in scanners:
        start_time_scanner = time.time()
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, sanitized_output)
        elapsed_time_scanner = time.time() - start_time_scanner
        logger.debug(
            f"Scanner {type(scanner).__name__}: Valid={is_valid}. Elapsed time: {elapsed_time_scanner:.6f} seconds"
        )

        results_valid[type(scanner).__name__] = is_valid
        results_score[type(scanner).__name__] = risk_score
        if fail_fast and not is_valid:
            break

    elapsed_time = time.time() - start_time
    logger.info(
        f"Scanned output with the score: {results_score}. Elapsed time: {elapsed_time:.6f} seconds"
    )

    return sanitized_output, results_valid, results_score
