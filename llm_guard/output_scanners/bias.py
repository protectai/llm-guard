from __future__ import annotations

from enum import Enum

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="valurank/distilroberta-bias",
    revision="c1e4a2773522c3acc929a7b2c9af2b7e4137b96d",
    onnx_path="ProtectAI/distilroberta-bias-onnx",
    onnx_revision="3e64d057d20d7ef43fa4f831b992bad28d72640e",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> list[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class Bias(Scanner):
    """
    This class is designed to detect and evaluate potential biases in text using a pretrained model from HuggingFace.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold: float = 0.7,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes the Bias scanner with a probability threshold for bias detection.

        Parameters:
           model (str): The model path to use for bias detection.
           threshold (float): The threshold above which a text is considered biased. Default is 0.7.
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

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, 0.0

        highest_score = 0.0
        results_all = self._classifier(self._match_type.get_inputs(prompt + "\n" + output))
        for result in results_all:
            score = round(
                result["score"] if result["label"] == "BIASED" else 1 - result["score"],
                2,
            )

            if score > highest_score:
                highest_score = score

            if score > self._threshold:
                LOGGER.warning(
                    "Detected biased text", highest_score=score, threshold=self._threshold
                )

                return output, False, calculate_risk_score(score, self._threshold)

        LOGGER.debug("Not biased result", highest_score=highest_score, threshold=self._threshold)

        return output, True, 0.0
