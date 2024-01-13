from enum import Enum
from typing import List, Union

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, logger, split_text_by_sentences

from .base import Scanner

_model_path = (
    "valurank/distilroberta-bias",
    "laiyer/distilroberta-bias-onnx",  # ONNX model
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
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
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes the Bias scanner with a probability threshold for bias detection.

        Parameters:
           threshold (float): The threshold above which a text is considered biased. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        self._classifier = pipeline(
            task="text-classification",
            model=_model_path[0],
            onnx_model=_model_path[1],
            truncation=True,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        highest_score = 0.0
        results_all = self._classifier(self._match_type.get_inputs(output))
        for result in results_all:
            score = round(
                result["score"] if result["label"] == "BIASED" else 1 - result["score"],
                2,
            )

            if score > highest_score:
                highest_score = score

            if score > self._threshold:
                logger.warning(
                    f"Detected biased text with score: {score}, threshold: {self._threshold}"
                )

                return output, False, calculate_risk_score(score, self._threshold)

        logger.debug(
            f"Not biased result. Highest score: {highest_score}, threshold: {self._threshold}"
        )

        return output, True, 0.0
