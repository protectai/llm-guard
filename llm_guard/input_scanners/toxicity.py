from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger(__name__)

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
        threshold: float = 0.5,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes Toxicity with a threshold for toxicity.

        Parameters:
           threshold (float): Threshold for toxicity. Default is 0.5.
           match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
           use_onnx (bool): Whether to use ONNX for inference. Default is False.
           transformers_kwargs (Optional[Dict]): Optional keyword arguments for the transformers pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["truncation"] = True
        transformers_kwargs["padding"] = "max_length"
        transformers_kwargs["top_k"] = None
        transformers_kwargs["function_to_apply"] = "sigmoid"

        self._pipeline = pipeline(
            task="text-classification",
            model=_model_path[0],
            onnx_model=_model_path[1],
            use_onnx=use_onnx,
            **transformers_kwargs,
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
