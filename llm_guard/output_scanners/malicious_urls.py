from typing import Dict, Optional

from llm_guard.transformers_helpers import pipeline
from llm_guard.util import calculate_risk_score, extract_urls, get_logger

from .base import Scanner

LOGGER = get_logger(__name__)
_model_path = (
    "DunnBC22/codebert-base-Malicious_URLs",
    "ProtectAI/codebert-base-Malicious_URLs-onnx",  # ONNX version
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
        self, *, threshold=0.5, use_onnx: bool = False, transformers_kwargs: Optional[Dict] = None
    ):
        """
        Initializes an instance of the MaliciousURLs class.

        Parameters:
            threshold (float): The threshold used to determine if the website is malicious. Defaults to 0.5.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
            transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """

        self._threshold = threshold

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = 512
        transformers_kwargs["truncation"] = True
        transformers_kwargs["top_k"] = None

        self._classifier = pipeline(
            task="text-classification",
            model=_model_path[0],
            onnx_model=_model_path[1],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        urls = extract_urls(output)
        if len(urls) == 0:
            return output, True, 0.0

        LOGGER.debug("Found URLs in the output", len=len(urls))

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
                    highest_malicious_score=highest_malicious_score,
                )

                return output, False, calculate_risk_score(highest_malicious_score, self._threshold)

        LOGGER.debug("Not malware URLs in the output", results=results)

        return output, True, 0.0
