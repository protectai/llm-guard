from __future__ import annotations

from enum import Enum
from typing import Dict, List

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger, split_text_by_sentences

from .base import Scanner

LOGGER = get_logger()

DEFAULT_MODEL = Model(
    path="SamLowe/roberta-base-go_emotions",
    revision="58b6c5b44a7a12093f782442969019c7e2982299",
    onnx_path="SamLowe/roberta-base-go_emotions-onnx",
    onnx_revision="90ee0c1c4796d370e68968687b8ba51fc11224f4",
    pipeline_kwargs={
        "padding": "max_length",
        "top_k": None,
        "function_to_apply": "sigmoid",
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

# 28 emotion labels from the go_emotions dataset
EMOTION_LABELS = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]

# Default list of negative emotions to block
DEFAULT_BLOCKED_EMOTIONS = [
    "anger",
    "annoyance",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "fear",
    "grief",
    "nervousness",
    "remorse",
    "sadness",
]


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> list[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)
        return [prompt]


class EmotionDetection(Scanner):
    """
    An emotion detection scanner that uses the roberta-base-go_emotions model to detect
    emotions in text. It can be configured to block specific emotions or detect high-intensity emotions.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold: float = 0.5,
        blocked_emotions: List[str] | None = None,
        match_type: MatchType | str = MatchType.FULL,
        use_onnx: bool = False,
        return_full_output: bool = False,
    ) -> None:
        """
        Initialize EmotionDetection scanner.

        Parameters:
            model (Model, optional): Model configuration. Defaults to DEFAULT_MODEL.
            threshold (float): Threshold for emotion detection. Defaults to 0.5.
            blocked_emotions (List[str], optional): List of emotions to block.
                If None, uses DEFAULT_BLOCKED_EMOTIONS (negative emotions).
            match_type (MatchType): Whether to match full text or individual sentences. Defaults to MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.
            return_full_output (bool): Whether to return full model output with all emotions and scores. Defaults to False.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._threshold = threshold
        self._match_type = match_type
        self._blocked_emotions = (
            blocked_emotions if blocked_emotions is not None else DEFAULT_BLOCKED_EMOTIONS
        )
        self._return_full_output = return_full_output

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

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if self._return_full_output:
            sanitized_prompt, is_valid, risk_score, emotion_analysis = self.scan_with_full_output(
                prompt
            )
            # Store the emotion analysis for later access if needed
            self._last_emotion_analysis = emotion_analysis
            return sanitized_prompt, is_valid, risk_score

        if prompt.strip() == "":
            return prompt, True, -1.0

        inputs = self._match_type.get_inputs(prompt)

        highest_emotion_score = 0.0
        emotions_above_threshold = []
        results_all = self._pipeline(inputs)

        for results_chunk in results_all:
            for result in results_chunk:
                emotion = result["label"]
                score = result["score"]

                # Skip neutral emotion
                if emotion == "neutral":
                    continue

                # Check if this emotion is blocked
                if emotion in self._blocked_emotions:
                    if score > self._threshold:
                        emotions_above_threshold.append(result)

                    if score > highest_emotion_score:
                        highest_emotion_score = score

        if len(emotions_above_threshold) > 0:
            LOGGER.warning(
                "Detected blocked emotions in the text",
                emotions=emotions_above_threshold,
                threshold=self._threshold,
            )
            return (
                prompt,
                False,
                calculate_risk_score(highest_emotion_score, self._threshold),
            )

        LOGGER.debug("No blocked emotions found in the text", results=results_all)
        return (
            prompt,
            True,
            0.0,
        )

    def get_emotion_analysis(self, prompt: str) -> Dict[str, float]:
        """
        Get full emotion analysis for the given prompt.

        Parameters:
            prompt (str): The input prompt to analyze.

        Returns:
            Dict[str, float]: Dictionary mapping emotion labels to their scores.
        """
        if prompt.strip() == "":
            return {}

        inputs = self._match_type.get_inputs(prompt)
        results_all = self._pipeline(inputs)

        # Aggregate scores across all inputs
        emotion_scores = {}
        for results_chunk in results_all:
            for result in results_chunk:
                emotion = result["label"]
                score = result["score"]

                # Use the highest score for each emotion if it appears multiple times
                if emotion not in emotion_scores or score > emotion_scores[emotion]:
                    emotion_scores[emotion] = score

        return emotion_scores

    def scan_with_full_output(self, prompt: str) -> tuple[str, bool, float, Dict[str, float]]:
        """
        Scan the prompt and return full emotion analysis along with the standard results.

        Parameters:
            prompt (str): The input prompt to scan.

        Returns:
            tuple[str, bool, float, Dict[str, float]]:
                - sanitized_prompt: The input prompt (unchanged)
                - is_valid: Whether the prompt is valid
                - risk_score: The risk score
                - emotion_analysis: Full emotion analysis with scores
        """
        if prompt.strip() == "":
            return prompt, True, -1.0, {}

        inputs = self._match_type.get_inputs(prompt)

        highest_emotion_score = 0.0
        emotions_above_threshold = []
        results_all = self._pipeline(inputs)

        # Get full emotion analysis
        emotion_analysis = {}
        for results_chunk in results_all:
            for result in results_chunk:
                emotion = result["label"]
                score = result["score"]

                # Store all emotion scores
                if emotion not in emotion_analysis or score > emotion_analysis[emotion]:
                    emotion_analysis[emotion] = score

                # Skip neutral emotion for blocking logic
                if emotion == "neutral":
                    continue

                # Check if this emotion is blocked
                if emotion in self._blocked_emotions:
                    if score > self._threshold:
                        emotions_above_threshold.append(result)

                    if score > highest_emotion_score:
                        highest_emotion_score = score

        if len(emotions_above_threshold) > 0:
            LOGGER.warning(
                "Detected blocked emotions in the text",
                emotions=emotions_above_threshold,
                threshold=self._threshold,
            )
            return (
                prompt,
                False,
                calculate_risk_score(highest_emotion_score, self._threshold),
                emotion_analysis,
            )

        LOGGER.debug("No blocked emotions found in the text", results=results_all)
        return (
            prompt,
            True,
            0.0,
            emotion_analysis,
        )
