from enum import Enum
from typing import List, Optional, Union

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

# This model is proprietary but open source.
DEFAULT_MODEL = Model(
    path="ProtectAI/deberta-v3-base-prompt-injection",
    revision="f51c3b2a5216ae1af467b511bc7e3b78dc4a99c9",
    onnx_path="ProtectAI/deberta-v3-base-prompt-injection",
    onnx_revision="f51c3b2a5216ae1af467b511bc7e3b78dc4a99c9",
    onnx_subfolder="onnx",
    onnx_filename="model.onnx",
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


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.
    """

    def __init__(
        self,
        *,
        model: Optional[Model] = None,
        threshold: float = 0.9,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
    ):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            model (Model, optional): Chosen model to classify prompt. Default is Laiyer's one.
            threshold (float): Threshold for the injection score. Default is 0.9.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.

        Raises:
            ValueError: If non-existent models were provided.
        """
        if model is None:
            model = DEFAULT_MODEL

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type
        self._model = model

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

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results_all = self._pipeline(self._match_type.get_inputs(prompt))
        for result in results_all:
            injection_score = round(
                result["score"] if result["label"] == "INJECTION" else 1 - result["score"],
                2,
            )

            if injection_score > highest_score:
                highest_score = injection_score

            if injection_score > self._threshold:
                LOGGER.warning("Detected prompt injection", injection_score=injection_score)

                return prompt, False, calculate_risk_score(injection_score, self._threshold)

        LOGGER.debug("No prompt injection detected", highest_score=highest_score)

        return prompt, True, 0.0
