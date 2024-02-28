from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

_model_path = (
    "valurank/distilroberta-bias",
    "ProtectAI/distilroberta-bias-onnx",  # ONNX model
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
        model_path: Optional[str] = None,
        threshold: float = 0.7,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Bias scanner with a probability threshold for bias detection.

        Parameters:
           model_path (str): The model path to use for bias detection.
           threshold (float): The threshold above which a text is considered biased. Default is 0.7.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
           model_kwargs (Dict, optional): Keyword arguments passed to the model.
           pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.
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

        onnx_model_path = model_path
        if model_path is None:
            model_path = _model_path[0]
            onnx_model_path = _model_path[1]

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path, onnx_model=onnx_model_path, use_onnx=use_onnx, **model_kwargs
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
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
                LOGGER.warning(
                    "Detected biased text", highest_score=score, threshold=self._threshold
                )

                return output, False, calculate_risk_score(score, self._threshold)

        LOGGER.debug("Not biased result", highest_score=highest_score, threshold=self._threshold)

        return output, True, 0.0
