from typing import List, Optional

from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

MODEL_BASE = "MoritzLaurer/deberta-v3-base-zeroshot-v1"
MODEL_LARGE = "MoritzLaurer/deberta-v3-large-zeroshot-v1"
ALL_MODELS = [MODEL_BASE, MODEL_LARGE]


class BanTopics(Scanner):
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(self, topics=List[str], threshold: float = 0.6, model: Optional[str] = MODEL_BASE):
        """
        Initialize BanTopics object.

        Args:
            topics (List[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (str, optional): Model to use for zero-shot classification. Default is deberta-v3-base-zeroshot-v1.

        Raises:
            ValueError: If no topics are provided.
        """
        if len(topics) == 0:
            raise ValueError("No topics provided")

        if model not in ALL_MODELS:
            raise ValueError(f"Model must be in the list of allowed: {ALL_MODELS}")

        self._topics = topics
        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._classifier = transformers.pipeline(
            "zero-shot-classification",
            model=model,
            device=device(),
            truncation=True,
        )
        logger.debug(f"Initialized model {model} on device {device()}")

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
