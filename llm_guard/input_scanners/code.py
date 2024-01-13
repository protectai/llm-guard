import re
from typing import List, Sequence

from llm_guard.exception import LLMGuardValidationError
from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, logger

from .base import Scanner

_model_path = (
    "huggingface/CodeBERTa-language-id",
    "laiyer/CodeBERTa-language-id-onnx",  # ONNX model
)

SUPPORTED_LANGUAGES = ["go", "java", "javascript", "php", "python", "ruby"]


class Code(Scanner):
    """
    A class for scanning if the prompt includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or block specific programming languages.
    """

    def __init__(
        self,
        languages: Sequence[str],
        *,
        is_blocked: bool = True,
        threshold: float = 0.5,
        use_onnx: bool = False,
    ):
        """
        Initializes Code with the allowed and denied languages.

        Parameters:
            languages (Sequence[str]): The list of programming languages to allow or deny.
            is_blocked (bool): Whether the languages are blocked or allowed. Default is True.
            threshold (float): The threshold for the risk score. Default is 0.5.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If both 'allowed' and 'denied' lists are provided or if both are empty.
        """
        if not set(languages).issubset(set(SUPPORTED_LANGUAGES)):
            raise LLMGuardValidationError(f"Languages must be a subset of {SUPPORTED_LANGUAGES}")

        self._languages = languages
        self._is_blocked = is_blocked
        self._threshold = threshold

        self._pipeline = pipeline(
            task="text-classification",
            model=_model_path[0],
            onnx_model=_model_path[1],
            use_onnx=use_onnx,
            truncation=True,
        )

        self._fenced_code_regex = re.compile(r"```(?:[a-zA-Z0-9]*\n)?(.*?)```", re.DOTALL)
        self._inline_code_regex = re.compile(r"`(.*?)`")

    def _extract_code_blocks(self, markdown: str) -> List[str]:
        # Extract fenced code blocks (between triple backticks)
        fenced_code_blocks = [
            block.strip() for block in self._fenced_code_regex.findall(markdown) if block.strip()
        ]

        # Extract inline code (between single backticks)
        inline_code = [
            code.strip()
            for code in self._inline_code_regex.findall(markdown)
            if code.strip() and any(char in code for char in "{}[]()=+-*/<>!")
        ]

        return fenced_code_blocks + inline_code

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        # Try to extract code snippets from Markdown
        code_blocks = self._extract_code_blocks(prompt)
        if len(code_blocks) == 0:
            logger.debug("No Markdown code blocks found in the output")
            return prompt, True, 0.0

        logger.debug(f"Code blocks found in the output: {code_blocks}")

        # Only check when the code is detected
        for code_block in code_blocks:
            languages = self._pipeline(code_block)
            logger.debug(f"Detected languages {languages} in the code: {code_block}")

            for language in languages:
                language_name = language["label"]
                score = round(language["score"], 2)

                if score < self._threshold or language_name not in self._languages:
                    continue

                if self._is_blocked:
                    logger.warning(f"Language {language_name} is not allowed (score {score})")
                    return prompt, False, calculate_risk_score(score, self._threshold)

                if not self._is_blocked:
                    logger.debug(f"Language {language_name} is allowed (score {score})")
                    return prompt, True, 0.0

        if self._is_blocked:
            logger.debug(f"No blocked languages detected")
            return prompt, True, 0.0

        logger.warning(f"No allowed languages detected")
        return prompt, False, 1.0
