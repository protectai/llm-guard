from __future__ import annotations

from enum import Enum

from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import (
    calculate_risk_score,
    get_logger,
    split_text_by_sentences,
    split_text_to_word_chunks,
    truncate_tokens_head_tail,
)

from .base import Scanner

LOGGER = get_logger()

PROMPT_CHARACTERS_LIMIT = 256

# This model is proprietary but open source.
V1_MODEL = Model(
    path="protectai/deberta-v3-base-prompt-injection",
    revision="f51c3b2a5216ae1af467b511bc7e3b78dc4a99c9",
    onnx_path="ProtectAI/deberta-v3-base-prompt-injection",
    onnx_revision="f51c3b2a5216ae1af467b511bc7e3b78dc4a99c9",
    onnx_subfolder="onnx",
    onnx_filename="model.onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

V2_MODEL = Model(
    path="protectai/deberta-v3-base-prompt-injection-v2",
    revision="89b085cd330414d3e7d9dd787870f315957e1e9f",
    onnx_path="ProtectAI/deberta-v3-base-prompt-injection-v2",
    onnx_revision="89b085cd330414d3e7d9dd787870f315957e1e9f",
    onnx_subfolder="onnx",
    onnx_filename="model.onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

# This is gated model, which requires our approval.
V2_SMALL_MODEL = Model(
    path="protectai/deberta-v3-small-prompt-injection-v2",
    revision="3897fe66d47d2e1649e669c3470bf2ba3ddecc22",
    onnx_path="protectai/deberta-v3-small-prompt-injection-v2",
    onnx_revision="3897fe66d47d2e1649e669c3470bf2ba3ddecc22",
    onnx_subfolder="onnx",
    onnx_filename="model.onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
    tokenizer_kwargs={
        "use_fast": False,
        "token": True,
    },
    kwargs={"token": True},  # You can also configure with your token.
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"
    # TRUNCATE_TOKEN_HEAD_TAIL is used to split the prompt into two parts (126 head and 382 tail) and check them.
    TRUNCATE_TOKEN_HEAD_TAIL = "truncate_token_head_tail"
    # TRUNCATE_SIDES is used to split the prompt into two parts (256 head and 256 tail) and check them.
    TRUNCATE_HEAD_TAIL = "truncate_head_tail"
    CHUNKS = "chunks"

    _tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast

    def set_tokenizer(self, tokenizer):
        self._tokenizer = tokenizer

    def get_inputs(self, prompt: str) -> list[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        if self == MatchType.CHUNKS:
            chunks = []
            for chunk_start, chunk_end in split_text_to_word_chunks(
                len(prompt), chunk_length=PROMPT_CHARACTERS_LIMIT, overlap_length=25
            ):
                chunks.append(prompt[chunk_start:chunk_end])

            return chunks

        if self == MatchType.TRUNCATE_TOKEN_HEAD_TAIL and self._tokenizer is not None:
            tokenized_input = self._tokenizer.tokenize(prompt)

            return [
                self._tokenizer.convert_tokens_to_string(truncate_tokens_head_tail(tokenized_input))
            ]

        if self == MatchType.TRUNCATE_HEAD_TAIL and len(prompt) > PROMPT_CHARACTERS_LIMIT:
            part_length = (PROMPT_CHARACTERS_LIMIT - 3) // 2

            start = prompt[:part_length]
            end = prompt[-part_length:]

            return [f"{start}...{end}"]

        return [prompt]


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold: float = 0.92,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            model (Model, optional): Chosen model to classify prompt. Default is Laiyer's one.
            threshold (float): Threshold for the injection score. Default is 0.9.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.

        Raises:
            ValueError: If non-existent models were provided.
        """
        if model is None:
            model = V2_MODEL

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._model = model

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

        match_type.set_tokenizer(tf_tokenizer)
        self._match_type = match_type

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results_all = self._pipeline(self._match_type.get_inputs(prompt))
        for result in results_all:
            injection_score = round(
                result["score"] if result["label"] == "INJECTION" else 1 - result["score"],
                2,
            )

            if injection_score > highest_score:
                highest_score = injection_score

            if injection_score > self._threshold:
                LOGGER.warning("Detected prompt injection", injection_score=injection_score)

                return prompt, False, calculate_risk_score(injection_score, self._threshold)

        LOGGER.debug("No prompt injection detected", highest_score=highest_score)

        return prompt, True, 0.0
