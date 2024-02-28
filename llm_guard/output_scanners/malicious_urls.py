from typing import Dict, Optional

from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, extract_urls, get_logger

from .base import Scanner

LOGGER = get_logger()
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
        self,
        *,
        model_path: Optional[str] = None,
        threshold=0.5,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the MaliciousURLs class.

        Parameters:
            model_path (str): The model path to use for malicious URL detection.
            threshold (float): The threshold used to determine if the website is malicious. Defaults to 0.5.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.
        """

        self._threshold = threshold

        default_pipeline_kwargs = {
            "max_length": 512,
            "truncation": True,
            "top_k": None,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        onnx_model_path = model_path
        if model_path is None:
            model_path = _model_path[0]
            onnx_model_path = _model_path[1]

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path, onnx_model=onnx_model_path, use_onnx=use_onnx, **model_kwargs
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
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
