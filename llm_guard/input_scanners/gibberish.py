from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

default_model_path = "madhurjindal/autonlp-Gibberish-Detector-492513457"


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
        model_path: str = default_model_path,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Gibberish scanner with a probability threshold for gibberish detection.

        Parameters:
           model_path (str): The path to the model.
           threshold (float): The probability threshold for gibberish detection. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
           model_kwargs (dict): Keyword arguments passed to the model.
           pipeline_kwargs (dict): Keyword arguments passed to the pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        default_pipeline_kwargs = {
            "truncation": True,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path, onnx_model=model_path, use_onnx=use_onnx, **model_kwargs
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
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
