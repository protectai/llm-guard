from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

_model_path = "ProtectAI/distilroberta-base-rejection-v1"


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
        model_path: str = _model_path,
        threshold: float = 0.75,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            model_path (str): The model path to use for scanning.
            threshold (float): The similarity threshold to consider an output as refusal.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.
        """

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        default_pipeline_kwargs = {
            "max_length": 512,
            "truncation": True,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path, onnx_model=model_path, use_onnx=use_onnx, **model_kwargs
        )

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
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
                LOGGER.warning("Detected rejection", highest_score=score)

                return output, False, calculate_risk_score(score, self._threshold)

        LOGGER.debug("No rejection detected", highest_score=highest_score)

        return output, True, 0.0
