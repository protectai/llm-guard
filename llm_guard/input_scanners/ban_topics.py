from typing import Dict, Optional, Sequence

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()

# This model was trained on a mixture of 33 datasets and 389 classes reformatted in the universal NLI format.
# The model is English only. You can also use it for multilingual zeroshot classification by first machine translating texts to English.
MODEL_LARGE = "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33"

# This is essentially the same as its larger sister MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33 only that it's smaller.
# Use it if you need more speed. The model is English-only.
MODEL_BASE = "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33"

# Same as above, just smaller/faster.
MODEL_XSMALL = "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33"


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
        model: Optional[str] = None,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initialize BanTopics object.

        Parameters:
            topics (Sequence[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (Dict, optional): Model to use for zero-shot classification. Default is deberta-v3-base-zeroshot-v1.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.

        Raises:
            ValueError: If no topics are provided.
        """
        if model is None:
            model = MODEL_BASE

        self._topics = topics
        self._threshold = threshold

        default_pipeline_kwargs = {
            "max_length": 512,
            "truncation": True,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model, onnx_model=model, use_onnx=use_onnx, **model_kwargs
        )

        self._classifier = pipeline(
            task="zero-shot-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        output_model = self._classifier(prompt, self._topics, multi_label=False)
        label_score = dict(zip(output_model["labels"], output_model["scores"]))

        max_score = round(max(output_model["scores"]) if output_model["scores"] else 0, 2)
        if max_score > self._threshold:
            LOGGER.warning(
                "Topics detected for the prompt",
                scores=label_score,
            )

            return prompt, False, max_score

        LOGGER.debug(
            "No banned topics detected",
            scores=label_score,
        )

        return prompt, True, 0.0
