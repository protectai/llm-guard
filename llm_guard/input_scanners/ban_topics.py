from __future__ import annotations

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger

from .base import Scanner

LOGGER = get_logger()

# The most performant model. 0.43 B parameters, 870 MB.
# It's English only. Context length max 512 tokens
MODEL_DEBERTA_LARGE_V2 = Model(
    path="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
    revision="cf44676c28ba7312e5c5f8f8d2c22b3e0c9cdae2",
    onnx_path="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
    onnx_revision="cf44676c28ba7312e5c5f8f8d2c22b3e0c9cdae2",
    onnx_subfolder="onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
    tokenizer_kwargs={
        "model_input_names": ["input_ids", "attention_mask"],
    },
)

# The most performant base model. 0.18 B parameters, 369 MB.
# It's English only. Context length max 512 tokens.
# Faster than RoBERTa-large/BGE-3 models, but slower than RoBERTa-base
MODEL_DEBERTA_BASE_V2 = Model(
    path="MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
    revision="8e7e5af5983a0ddb1a5b45a38b129ab69e2258e8",
    onnx_path="MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
    onnx_subfolder="onnx",
    onnx_revision="8e7e5af5983a0ddb1a5b45a38b129ab69e2258e8",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
    tokenizer_kwargs={
        "model_input_names": ["input_ids", "attention_mask"],
    },
)

# The most performance multilingual model. 0.57 B parameters, 1.14 GB.
# 100+ languages; context length max 8192 tokens; based on bge-m3-retromae, which is based on XLM-RoBERTa
MODEL_BGE_M3_V2 = Model(
    path="MoritzLaurer/bge-m3-zeroshot-v2.0",
    revision="cd3f8598c7359a3b5cbce164d7fcdafb83a36484",
    onnx_path="MoritzLaurer/bge-m3-zeroshot-v2.0",
    onnx_subfolder="onnx",
    onnx_revision="cd3f8598c7359a3b5cbce164d7fcdafb83a36484",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

# Less performant than deberta-v3 variants, but a bit faster and compatible with flash attention and TEI containers.
# Size: 0.35B parameters, 711 MB. It's English only. Context length max 512 tokens.
# Only trained on commercially-friendly data.
MODEL_ROBERTA_LARGE_C_V2 = Model(
    path="MoritzLaurer/roberta-large-zeroshot-v2.0-c",
    revision="4c24ed4bba5af8d3162604abc2a141b9d2183ecc",
    onnx_path="MoritzLaurer/roberta-large-zeroshot-v2.0-c",
    onnx_subfolder="onnx",
    onnx_revision="4c24ed4bba5af8d3162604abc2a141b9d2183ecc",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)

# Same model but smaller, more efficient version.
MODEL_ROBERTA_BASE_C_V2 = Model(
    path="MoritzLaurer/roberta-base-zeroshot-v2.0-c",
    revision="d825e740e0c59881cf0b0b1481ccf726b6d65341",
    onnx_path="protectai/MoritzLaurer-roberta-base-zeroshot-v2.0-c-onnx",
    onnx_revision="fde5343dbad32f1a5470890505c72ec656db6dbe",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    },
)


class BanTopics(Scanner):
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(
        self,
        topics: list[str],
        *,
        threshold: float = 0.6,
        model: Model | None = None,
        use_onnx: bool = False,
    ) -> None:
        """
        Initialize BanTopics object.

        Parameters:
            topics (Sequence[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (Model, optional): Model to use for zero-shot classification. Default is roberta-base-c-v2.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If no topics are provided.
        """
        self._topics = topics
        self._threshold = threshold

        if model is None:
            model = MODEL_ROBERTA_BASE_C_V2

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )

        self._classifier = pipeline(
            task="zero-shot-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
        )

    def scan(self, prompt: str) -> tuple[str, bool, float]:
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

            return prompt, False, calculate_risk_score(max_score, self._threshold)

        LOGGER.debug(
            "No banned topics detected",
            scores=label_score,
        )

        return prompt, True, 0.0
