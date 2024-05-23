from __future__ import annotations

import re

from llm_guard.exception import LLMGuardValidationError
from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger

from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="philomath-1209/programming-language-identification",
    revision="9090d38e7333a2c6ff00f154ab981a549842c20f",
    onnx_path="philomath-1209/programming-language-identification",
    onnx_revision="9090d38e7333a2c6ff00f154ab981a549842c20f",
    onnx_subfolder="onnx",
    pipeline_kwargs={
        "top_k": None,
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

SUPPORTED_LANGUAGES = [
    "ARM Assembly",
    "AppleScript",
    "C",
    "C#",
    "C++",
    "COBOL",
    "Erlang",
    "Fortran",
    "Go",
    "Java",
    "JavaScript",
    "Kotlin",
    "Lua",
    "Mathematica/Wolfram Language",
    "PHP",
    "Pascal",
    "Perl",
    "PowerShell",
    "Python",
    "R",
    "Ruby",
    "Rust",
    "Scala",
    "Swift",
    "Visual Basic .NET",
    "jq",
]


class Code(Scanner):
    """
    A class for scanning if the prompt includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or block specific programming languages.
    """

    def __init__(
        self,
        languages: list[str],
        *,
        model: Model | None = None,
        is_blocked: bool = True,
        threshold: float = 0.5,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes Code with the allowed and denied languages.

        Parameters:
            model: The model to use for language detection.
            languages: The list of programming languages to allow or deny.
            is_blocked: Whether the languages are blocked or allowed. Default is True.
            threshold: The threshold for the risk score. Default is 0.5.
            use_onnx: Whether to use ONNX for inference. Default is False.

        Raises:
            LLMGuardValidationError: If the languages are not a subset of SUPPORTED_LANGUAGES.
        """
        if not set(languages).issubset(set(SUPPORTED_LANGUAGES)):
            raise LLMGuardValidationError(f"Languages must be a subset of {SUPPORTED_LANGUAGES}")

        self._languages = languages
        self._is_blocked = is_blocked
        self._threshold = threshold

        if model is None:
            model = DEFAULT_MODEL

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
        )

        self._fenced_code_regex = re.compile(r"```(?:[a-zA-Z0-9]*\n)?(.*?)```", re.DOTALL)
        self._inline_code_regex = re.compile(r"`(.*?)`")

    def _extract_code_blocks(self, markdown: str) -> list[str]:
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

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if prompt.strip() == "":
            return prompt, True, 0.0

        # Try to extract code snippets from Markdown
        code_blocks = self._extract_code_blocks(prompt)
        if len(code_blocks) == 0:
            LOGGER.debug(
                "No Markdown code blocks found in the output. Using the whole input as code."
            )
            code_blocks = [prompt]

        LOGGER.debug("Code blocks found in the output", code_blocks=code_blocks)

        # Only check when the code is detected
        results = self._pipeline(code_blocks)
        for code_block, languages in zip(code_blocks, results):
            LOGGER.debug(
                "Detected languages in the code", languages=languages, code_block=code_block
            )

            for language in languages:
                score = round(language["score"], 2)

                if score < self._threshold or language["label"] not in self._languages:
                    continue

                if self._is_blocked:
                    LOGGER.warning(
                        "Language is not allowed", language_name=language["label"], score=score
                    )
                    return prompt, False, calculate_risk_score(score, self._threshold)

                if not self._is_blocked:
                    LOGGER.debug(
                        "Language is allowed", language_name=language["label"], score=score
                    )
                    return prompt, True, 0.0

        if self._is_blocked:
            LOGGER.debug("No blocked languages detected")
            return prompt, True, 0.0

        LOGGER.warning("No allowed languages detected")
        return prompt, False, 1.0
