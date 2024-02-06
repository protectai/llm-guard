from enum import Enum
from typing import Dict, List, Optional, Sequence, Union

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger(__name__)

model_path = (
    "papluca/xlm-roberta-base-language-detection",
    "ProtectAI/xlm-roberta-base-language-detection-onnx",
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class Language(Scanner):
    """
    A Scanner subclass responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.

    Note: when no languages are detected above the threshold, the prompt is considered valid.
    """

    def __init__(
        self,
        valid_languages: Sequence[str],
        *,
        threshold: float = 0.6,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (Sequence[str]): A list of valid language codes in ISO 639-1.
            threshold (float): Minimum confidence score.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            transformers_kwargs (Optional[Dict]): Optional keyword arguments for the transformers pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._valid_languages = valid_languages
        self._match_type = match_type

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = 512
        transformers_kwargs["truncation"] = True
        transformers_kwargs["top_k"] = None

        self._pipeline = pipeline(
            task="text-classification",
            model=model_path[0],
            onnx_model=model_path[1],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        results_all = self._pipeline(self._match_type.get_inputs(prompt))
        for result_chunk in results_all:
            languages_above_threshold = [
                result["label"] for result in result_chunk if result["score"] > self._threshold
            ]

            highest_score = max([result["score"] for result in result_chunk])

            # Check if any of the languages above threshold are not valid
            if len(set(languages_above_threshold) - set(self._valid_languages)) > 0:
                LOGGER.warning(
                    "Languages are found with high confidence", languages=languages_above_threshold
                )

                return prompt, False, calculate_risk_score(highest_score, self._threshold)

        LOGGER.debug("Only valid languages are found in the text.")

        return prompt, True, 0.0
