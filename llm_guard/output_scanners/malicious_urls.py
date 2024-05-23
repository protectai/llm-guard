from __future__ import annotations

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, extract_urls, get_logger

from .base import Scanner

LOGGER = get_logger()
DEFAULT_MODEL = Model(
    path="DunnBC22/codebert-base-Malicious_URLs",
    revision="1221284b2495a4182cdb521be9d755de56e66899",
    onnx_path="ProtectAI/codebert-base-Malicious_URLs-onnx",
    onnx_revision="7bc4fa926eeae5e752d0790cc42faa24eb32fa64",
    pipeline_kwargs={
        "top_k": None,
        "return_token_type_ids": False,
        "max_length": 128,
        "truncation": True,
    },
)

_malicious_labels = [
    "defacement",
    "phishing",
    "malware",
]


class MaliciousURLs(Scanner):
    """
    This scanner is used to scan and detect malicious URLs in the text.

    Large Language Models can occasionally produce malicious URLs in their outputs.
    Using the "DunnBC22/codebert-base-Malicious_URLs" model from HuggingFace, this class classifies
    URLs as either malicious or benign to safeguard users from potential threats.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        threshold=0.5,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes an instance of the MaliciousURLs class.

        Parameters:
            model (Model, optional): The model to use for malicious URL detection.
            threshold (float): The threshold used to determine if the website is malicious. Defaults to 0.5.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._threshold = threshold

        if model is None:
            model = DEFAULT_MODEL

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, 0.0

        urls = extract_urls(output)
        if len(urls) == 0:
            return output, True, 0.0

        LOGGER.debug("Found URLs in the output", len=len(urls))

        highest_malicious_score = 0.0
        results = self._classifier(urls)
        for url, result in zip(urls, results):
            malicious_scores = [
                item["score"] for item in result if item["label"] in _malicious_labels
            ]
            highest_malicious_score = max(malicious_scores)
            if highest_malicious_score > self._threshold:
                LOGGER.warning(
                    "Detected malware URL",
                    url=url,
                    highest_score=highest_malicious_score,
                )

                return output, False, calculate_risk_score(highest_malicious_score, self._threshold)

        LOGGER.debug(
            "Not malware URLs in the output", results=results, highest_score=highest_malicious_score
        )

        return output, True, 0.0
