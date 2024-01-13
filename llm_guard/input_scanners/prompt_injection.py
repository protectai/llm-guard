from enum import Enum
from typing import Dict, List, Optional, Union

from llm_guard.exception import LLMGuardValidationError
from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, logger, split_text_by_sentences

from .base import Scanner

# This model is proprietary but open source.
MODEL_LAIYER = {
    "path": "laiyer/deberta-v3-base-prompt-injection",
    "onnx_path": "laiyer/deberta-v3-base-prompt-injection",  # extract from onnx folder
    "label": "INJECTION",
    "max_length": 512,
}

ALL_MODELS = [
    MODEL_LAIYER,
]


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.
    """

    def __init__(
        self,
        *,
        model: Optional[Dict] = None,
        threshold: float = 0.9,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            model (Dict, optional): Chosen model to classify prompt. Default is Laiyer's one.
            threshold (float): Threshold for the injection score. Default is 0.9.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.

        Raises:
            ValueError: If non-existent models were provided.
        """
        if model is None:
            model = MODEL_LAIYER

        if model not in ALL_MODELS:
            raise LLMGuardValidationError(f"Model must be in the list of allowed: {ALL_MODELS}")

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type
        self._model = model
        self._pipeline = pipeline(
            task="text-classification",
            model=model["path"],
            use_onnx=use_onnx,
            onnx_model=model["onnx_path"],
            truncation=True,
            max_length=model["max_length"],
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results_all = self._pipeline(self._match_type.get_inputs(prompt))
        for result in results_all:
            injection_score = round(
                result["score"] if result["label"] == self._model["label"] else 1 - result["score"],
                2,
            )

            if injection_score > highest_score:
                highest_score = injection_score

            if injection_score > self._threshold:
                logger.warning(f"Detected prompt injection with score: {injection_score}")

                return prompt, False, calculate_risk_score(injection_score, self._threshold)

        logger.debug(f"No prompt injection detected, highest score: {highest_score}")

        return prompt, True, 0.0
