import logging
import re
from typing import List, Optional

from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizer,
    TextClassificationPipeline,
)

from llm_guard.util import device

from .base import Scanner

log = logging.getLogger(__name__)
model_name = "huggingface/CodeBERTa-language-id"

SUPPORTED_LANGUAGES = ["go", "java", "javascript", "php", "python", "ruby"]

_fenced_code_regex = re.compile(r"```(?:[a-zA-Z0-9]*\n)?(.*?)```", re.DOTALL)
_inline_code_regex = re.compile(r"`(.*?)`")


def _extract_code_blocks(markdown: str) -> List[str]:
    # Extract fenced code blocks (between triple backticks)
    fenced_code_blocks = [
        block.strip() for block in _fenced_code_regex.findall(markdown) if block.strip()
    ]

    # Extract inline code (between single backticks)
    inline_code = [
        code.strip()
        for code in _inline_code_regex.findall(markdown)
        if code.strip() and any(char in code for char in "{}[]()=+-*/<>!")
    ]

    return fenced_code_blocks + inline_code


def is_language_detected(
    text: str,
    pipeline: TextClassificationPipeline,
    allowed: List[str],
    denied: List[str],
    threshold: float,
) -> (bool, float):
    """
    Checks whether the text contains languages listed in the 'allowed' or 'denied' lists.

    Parameters:
        text (str): The text to check.
        pipeline (TextClassificationPipeline): The Huggingface pipeline for text classification.
        allowed (List[str]): A list of allowed languages.
        denied (List[str]): A list of denied languages.
        threshold (float): The threshold for the risk score.

    Returns:
        bool: True if the text contains allowed languages or doesn't contain denied languages. False otherwise.
        float: Risk score, where 0 is no risk and 1 is the highest risk.
    """
    if text.strip() == "":
        return True, 0.0

    # Try to extract code snippets from Markdown
    code_blocks = _extract_code_blocks(text)
    if len(code_blocks) == 0:
        log.debug("No Markdown code blocks found in the output")
        return True, 0.0

    log.debug(f"Code blocks found in the output: {code_blocks}")

    # Only check when the code is detected
    for code_block in code_blocks:
        languages = pipeline(code_block)
        log.debug(f"Detected languages {languages} in the block {code_block}")

        for language in languages:
            language_name = language["label"]
            score = round(language["score"], 2)

            if score < threshold:
                continue

            if len(allowed) > 0 and language_name in allowed:
                log.debug(f"Language {language_name} found in the allowed list with score {score}")
                return True, 0.0

            if len(denied) > 0 and language_name in denied:
                log.warning(f"Language {language_name} is not allowed (score {score})")
                return False, score

    if len(allowed) > 0:
        log.warning(f"No allowed languages detected")
        return False, 1.0

    log.debug(f"No denied languages detected")

    return True, 0.0


class Code(Scanner):
    """
    A class for scanning if the prompt includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or deny specific programming languages.
    """

    def __init__(
        self,
        allowed: Optional[List[str]] = None,
        denied: Optional[List[str]] = None,
        threshold: float = 0.5,
    ):
        """
        Initializes Code with the allowed and denied languages.

        Parameters:
            allowed (Optional[List[str]]): A list of allowed languages. Default is an empty list.
            denied (Optional[List[str]]): A list of denied languages. Default is an empty list.
            threshold (float): The threshold for the risk score. Default is 0.5.

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

        if len(allowed) > 0 and not set(allowed).issubset(set(SUPPORTED_LANGUAGES)):
            raise ValueError(f"Allowed languages must be a subset of {SUPPORTED_LANGUAGES}")

        if len(denied) > 0 and not set(denied).issubset(set(SUPPORTED_LANGUAGES)):
            raise ValueError(f"Denied languages must be a subset of {SUPPORTED_LANGUAGES}")

        self._allowed = allowed
        self._denied = denied
        self._threshold = threshold
        self._pipeline = TextClassificationPipeline(
            model=RobertaForSequenceClassification.from_pretrained(model_name),
            tokenizer=RobertaTokenizer.from_pretrained(model_name),
            device=device,
        )
        log.debug(f"Initialized model {model_name} on device {device}")

    def scan(self, prompt: str) -> (str, bool, float):
        valid, score = is_language_detected(
            prompt, self._pipeline, self._allowed, self._denied, self._threshold
        )
        return prompt, valid, score
