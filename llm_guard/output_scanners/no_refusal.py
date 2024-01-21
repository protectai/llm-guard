from enum import Enum
from typing import List, Union

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, logger, split_text_by_sentences

from .base import Scanner

_model = {
    "path": "laiyer/distilroberta-base-rejection-v1",
    "onnx_path": "laiyer/distilroberta-base-rejection-v1",
    "max_length": 512,
}


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class NoRefusal(Scanner):
    """
    A class used to detect and handle refusals in language model output.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.75,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            threshold (float): The similarity threshold to consider an output as refusal.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type
        self._pipeline = pipeline(
            task="text-classification",
            model=_model["path"],
            onnx_model=_model["onnx_path"],
            use_onnx=use_onnx,
            max_length=_model["max_length"],
            truncation=True,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        highest_score = 0.0
        results_all = self._pipeline(self._match_type.get_inputs(output))
        for result in results_all:
            score = round(
                result["score"] if result["label"] == "REJECTION" else 1 - result["score"],
                2,
            )

            if score > highest_score:
                highest_score = score

            if score > self._threshold:
                logger.warning(f"Detected rejection with score: {score}")

                return output, False, calculate_risk_score(score, self._threshold)

        logger.debug(f"No rejection detected, highest score: {highest_score}")

        return output, True, 0.0
