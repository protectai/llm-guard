import importlib
import json
import logging
from functools import lru_cache
from typing import Dict, List, Optional

logger = logging.getLogger("llm-guard")

"""
This file contains utility functions.
This is meant for internal use and not part of the public API.
"""


# Detect pytorch device
@lru_cache(maxsize=None)  # Unbounded cache
def device():
    torch = lazy_load_dep("torch")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        device = torch.device("mps")
    return device


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
            logger.debug(f"Loaded json file {json_path}")
    except FileNotFoundError:
        logger.error(f"Could not find {json_path}")
    except json.decoder.JSONDecodeError as json_error:
        logger.error(f"Could not parse {json_path}: {json_error}")
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
        logger.warning(
            f"Optional feature dependent on missing package: {import_name} was initialized.\n"
            f"Use `pip install {package_name}` to install the package if running locally."
        )

    return importlib.import_module(import_name)
