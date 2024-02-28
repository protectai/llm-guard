from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

_model_path = (
    "unitary/unbiased-toxic-roberta",
    "ProtectAI/unbiased-toxic-roberta-onnx",  # ONNX model
)
_toxic_labels = [
    "toxicity",
    "severe_toxicity",
    "obscene",
    "threat",
    "insult",
    "identity_attack",
    "sexual_explicit",
]


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class Toxicity(Scanner):
    """
    A toxicity scanner that uses a pretrained Hugging Face model to assess the toxicity of a given text.

    If the toxicity score is less than a predefined threshold, the text is considered non-toxic. Otherwise, it is
    considered toxic.
    """

    def __init__(
        self,
        *,
        model_path: Optional[str] = None,
        threshold: float = 0.5,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes Toxicity with a threshold for toxicity.

        Parameters:
           model_path (str, optional): Path to the model. Default is None.
           threshold (float): Threshold for toxicity. Default is 0.5.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX for inference. Default is False.
           model_kwargs (Dict, optional): Keyword arguments passed to the model.
           pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        default_pipeline_kwargs = {
            "padding": "max_length",
            "top_k": None,
            "function_to_apply": "sigmoid",
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

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        inputs = self._match_type.get_inputs(prompt)

        highest_toxicity_score = 0.0
        toxicity_above_threshold = []
        results_all = self._pipeline(inputs)
        for results_chunk in results_all:
            for result in results_chunk:
                if result["label"] not in _toxic_labels:
                    continue

                if result["score"] > self._threshold:
                    toxicity_above_threshold.append(result)

                if result["score"] > highest_toxicity_score:
                    highest_toxicity_score = result["score"]

        if len(toxicity_above_threshold) > 0:
            LOGGER.warning("Detected toxicity in the text", results=toxicity_above_threshold)

            return prompt, False, calculate_risk_score(highest_toxicity_score, self._threshold)

        LOGGER.debug("Not toxicity found in the text", results=results_all)

        return prompt, True, 0.0
