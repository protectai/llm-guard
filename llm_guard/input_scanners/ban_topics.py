from typing import Dict, Optional, Sequence

from llm_guard.exception import LLMGuardValidationError
from llm_guard.transformers_helpers import pipeline
from llm_guard.util import logger

from .base import Scanner

# This model was trained on a mixture of 33 datasets and 389 classes reformatted in the universal NLI format.
# The model is English only. You can also use it for multilingual zeroshot classification by first machine translating texts to English.
MODEL_LARGE = {
    "path": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# This is essentially the same as its larger sister MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33 only that it's smaller.
# Use it if you need more speed. The model is English-only.
MODEL_BASE = {
    "path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# Same as above, just smaller/faster.
MODEL_XSMALL = {
    "path": "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# Same as above, just even faster. The model only has 22 million backbone parameters.
# The model is 25 MB small (or 13 MB with ONNX quantization).
MODEL_XTREMEDISTIL = {
    "path": "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33",
    "max_length": 512,
}

ALL_MODELS = [MODEL_LARGE, MODEL_BASE, MODEL_XSMALL, MODEL_XTREMEDISTIL]


class BanTopics(Scanner):
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(
        self,
        topics: Sequence[str],
        *,
        threshold: float = 0.6,
        model: Optional[Dict] = None,
        use_onnx: bool = False,
    ):
        """
        Initialize BanTopics object.

        Parameters:
            topics (Sequence[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (Dict, optional): Model to use for zero-shot classification. Default is deberta-v3-base-zeroshot-v1.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If no topics are provided.
        """
        if model is None:
            model = MODEL_BASE

        if model not in ALL_MODELS:
            raise LLMGuardValidationError(f"Model must be in the list of allowed: {ALL_MODELS}")

        self._topics = topics
        self._threshold = threshold

        self._classifier = pipeline(
            task="zero-shot-classification",
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
