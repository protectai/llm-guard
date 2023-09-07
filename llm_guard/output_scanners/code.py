import logging
from typing import List, Optional

from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizer,
    TextClassificationPipeline,
)

from llm_guard.input_scanners.code import is_language_detected, model_name
from llm_guard.util import device

from .base import Scanner

log = logging.getLogger(__name__)


class Code(Scanner):
    """
    A class for scanning if the model output includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or deny specific programming languages.
    """

    def __init__(self, allowed: Optional[List[str]] = None, denied: Optional[List[str]] = None):
        """
        Initializes an instance of the Code class.

        Parameters:
            allowed (Optional[List[str]]): A list of programming languages that are allowed in the model output.
            denied (Optional[List[str]]): A list of programming languages that are not allowed in the model output.

        Raises:
            ValueError: If both 'allowed' and 'denied' lists are provided or if both are empty.
        """

        if not allowed:
            allowed = []

        if not denied:
            denied = []

        if len(allowed) > 0 and len(denied) > 0:
            raise ValueError("Provide either allowed or denied programming languages")

        if len(allowed) == 0 and len(denied) == 0:
            raise ValueError("No allowed or denied programming languages provided")

        self._allowed = allowed
        self._denied = denied
        self._pipeline = TextClassificationPipeline(
            model=RobertaForSequenceClassification.from_pretrained(model_name),
            tokenizer=RobertaTokenizer.from_pretrained(model_name),
            device=device,
        )
        log.debug(f"Initialized model {model_name} on device {device}")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        valid, score = is_language_detected(output, self._pipeline, self._allowed, self._denied)
        return output, valid, score
