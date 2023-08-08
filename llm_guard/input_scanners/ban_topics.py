import logging
from typing import List

from transformers import pipeline

from .base import Scanner

_model_path = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

log = logging.getLogger(__name__)


class BanTopics(Scanner):
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(self, topics=List[str], threshold: float = 0.75):
        """
        Initialize BanTopics object.

        Args:
            topics (List[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.

        Raises:
            ValueError: If no topics are provided.
        """
        if len(topics) == 0:
            raise ValueError("No topics provided")

        self._topics = topics
        self._threshold = threshold
        self._classifier = pipeline("zero-shot-classification", model=_model_path)

    def scan(self, prompt: str) -> (str, bool):
        if prompt.strip() == "":
            return prompt, True

        output = self._classifier(prompt, self._topics, multi_label=False)

        max_score = max(output["scores"]) if output["scores"] else 0
        if max_score > self._threshold:
            log.warning(
                f"Topics detected for the prompt {output['labels']} with scores: {output['scores']}"
            )

            return prompt, False

        log.debug(f"No banned topics detected ({output['labels']}, scores: {output['scores']})")

        return prompt, True
