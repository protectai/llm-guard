from enum import Enum
from typing import List, Optional, Union

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
        model: Optional[Model] = None,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
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
