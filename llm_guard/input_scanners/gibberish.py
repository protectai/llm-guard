from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger(__name__)

_model_path = (
    "madhurjindal/autonlp-Gibberish-Detector-492513457",
    "ProtectAI/madhurjindal-autonlp-Gibberish-Detector-492513457-onnx",  # ONNX model
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
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
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
           transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["truncation"] = True

        self._classifier = pipeline(
            task="text-classification",
            model=_model_path[0],
            onnx_model=_model_path[1],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results_all = self._classifier(self._match_type.get_inputs(prompt))
        LOGGER.debug("Gibberish detection finished", results=results_all)
        for result in results_all:
            score = round(
                1 - result["score"] if result["label"] == "clean" else result["score"],
                2,
            )

            if score > highest_score:
                highest_score = score

            if score > self._threshold:
                LOGGER.warning("Detected gibberish text", score=score, threshold=self._threshold)

                return prompt, False, calculate_risk_score(score, self._threshold)

        LOGGER.debug(
            "No gibberish in the text", highest_score=highest_score, threshold=self._threshold
        )

        return prompt, True, 0.0
