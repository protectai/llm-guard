import json
import logging
from typing import Dict, List

from accelerate import Accelerator

log = logging.getLogger(__name__)

"""
This file contains utility functions.
This is meant for internal use and not part of the public API.
"""

# Detect pytorch device
accelerator = Accelerator()
device = accelerator.device
device_int = 0 if device.type == "cuda" else -1


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
            log.debug(f"Loaded json file {json_path}")
    except FileNotFoundError:
        log.error(f"Could not find {json_path}")
    except json.decoder.JSONDecodeError as json_error:
        log.error(f"Could not parse {json_path}: {json_error}")
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
