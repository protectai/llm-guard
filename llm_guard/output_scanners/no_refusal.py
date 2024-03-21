from enum import Enum
from typing import List, Optional, Union

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="ProtectAI/distilroberta-base-rejection-v1",
    onnx_path="ProtectAI/distilroberta-base-rejection-v1-onnx",
    onnx_subfolder="onnx",
    pipeline_kwargs={
        "max_length": 512,
        "truncation": True,
    },
)


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
        model: Optional[Model] = None,
        threshold: float = 0.75,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            model (Model, optional): The model to use for refusal detection.
            threshold (float): The similarity threshold to consider an output as refusal.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
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

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
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
