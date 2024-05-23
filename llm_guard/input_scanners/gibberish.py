from __future__ import annotations

from enum import Enum

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="madhurjindal/autonlp-Gibberish-Detector-492513457",
    revision="fddf42c3008ad61cc481f90d02dd0712ba1ee2d8",
    onnx_path="madhurjindal/autonlp-Gibberish-Detector-492513457",
    onnx_revision="fddf42c3008ad61cc481f90d02dd0712ba1ee2d8",
    onnx_subfolder="onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

_gibberish_labels = ["word salad", "noise", "mild gibberish"]


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> list[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class Gibberish(Scanner):
    """
    A scanner that detects gibberish text.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold: float = 0.97,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           model (Model, optional): The model object.
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        if model is None:
            model = DEFAULT_MODEL

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
        )

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results_all = self._classifier(self._match_type.get_inputs(prompt))
        LOGGER.debug("Gibberish detection finished", results=results_all)
        for result in results_all:
            score = round(
                result["score"] if result["label"] in _gibberish_labels else 1 - result["score"],
                2,
            )

            if score > highest_score:
                highest_score = score

        if highest_score > self._threshold:
            LOGGER.warning(
                "Detected gibberish text", score=highest_score, threshold=self._threshold
            )

            return prompt, False, calculate_risk_score(highest_score, self._threshold)

        LOGGER.debug(
            "No gibberish in the text", highest_score=highest_score, threshold=self._threshold
        )

        return prompt, True, 0.0
