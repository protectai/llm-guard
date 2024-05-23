from __future__ import annotations

from enum import Enum

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .ban_substrings import BanSubstrings, MatchType as BanSubstringsMatchType
from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="ProtectAI/distilroberta-base-rejection-v1",
    revision="65584967c3f22ff7723e5370c65e0e76791e6055",
    onnx_path="ProtectAI/distilroberta-base-rejection-v1",
    onnx_revision="65584967c3f22ff7723e5370c65e0e76791e6055",
    onnx_subfolder="onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 128,
        "truncation": True,
    },
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> list[str]:
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
        model: Model | None = None,
        threshold: float = 0.75,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
    ) -> None:
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

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
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


class NoRefusalLight(BanSubstrings):
    """
    A class used to detect and handle refusals in language model output.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(self):
        super().__init__(
            substrings=[
                "I'm sorry",
                "Sorry",
                "I am sorry",
                "I apologize",
                "As an",
                "As an AI",
                "I'm an",
                "I'm just",
                "As a language model",
                "As an Assistant",
                "I cannot",
                "I do not",
                "Hello!",
                "is illegal and unethical",
                "I'm really sorry",
                "OpenAI",
                "unethical",
                "not ethical",
                "not legal",
                "My apologies",
                "but I cannot",
                "If you have any other non-malicious requests",
                "I'm not able to provide",
                "I am really sorry",
                "I cannot create",
                "I cannot support",
                "I can't provide",
                "I can't assist",
            ],
            match_type=BanSubstringsMatchType.STR,
            case_sensitive=False,
            redact=False,
            contains_all=False,
        )
