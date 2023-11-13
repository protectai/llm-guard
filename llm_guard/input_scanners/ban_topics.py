from typing import Dict, List, Optional

from llm_guard.transformers_helpers import pipeline_zero_shot_classification
from llm_guard.util import logger

from .base import Scanner

MODEL_BASE = {
    "path": "MoritzLaurer/deberta-v3-base-zeroshot-v1",
    "onnx_path": "laiyer/deberta-v3-base-zeroshot-v1-onnx",
    "max_length": 512,
}
MODEL_LARGE = {
    "path": "MoritzLaurer/deberta-v3-large-zeroshot-v1",
    "onnx_path": "laiyer/deberta-v3-large-zeroshot-v1-onnx",
    "max_length": 512,
}
ALL_MODELS = [MODEL_BASE, MODEL_LARGE]


class BanTopics(Scanner):
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(
        self,
        topics=List[str],
        threshold: float = 0.6,
        model: Optional[Dict] = None,
        use_onnx: bool = False,
    ):
        """
        Initialize BanTopics object.

        Args:
            topics (List[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (Dict, optional): Model to use for zero-shot classification. Default is deberta-v3-base-zeroshot-v1.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If no topics are provided.
        """
        if len(topics) == 0:
            raise ValueError("No topics provided")

        if model is None:
            model = MODEL_BASE

        if model not in ALL_MODELS:
            raise ValueError(f"Model must be in the list of allowed: {ALL_MODELS}")

        self._topics = topics
        self._threshold = threshold

        self._classifier = pipeline_zero_shot_classification(
            model=model["path"],
            onnx_model=model["onnx_path"],
            use_onnx=use_onnx,
            max_length=model["max_length"],
            truncation=True,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        output_model = self._classifier(prompt, self._topics, multi_label=False)

        max_score = round(max(output_model["scores"]) if output_model["scores"] else 0, 2)
        if max_score > self._threshold:
            logger.warning(
                f"Topics detected for the prompt {output_model['labels']} with scores: {output_model['scores']}"
            )

            return prompt, False, max_score

        logger.debug(
            f"No banned topics detected ({output_model['labels']}, scores: {output_model['scores']})"
        )

        return prompt, True, 0.0
