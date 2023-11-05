import re
from typing import List

from llm_guard.transformers_helpers import pipeline_text_classification
from llm_guard.util import logger

from .base import Scanner

_model_path = "elftsdmr/malware-url-detect"

# URL pattern
url_pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


class MaliciousURLs(Scanner):
    """
    This scanner is used to scan and detect malicious URLs in the text.

    Large Language Models can occasionally produce malicious URLs in their outputs.
    Using the "elftsdmr/malware-url-detect" model from HuggingFace, this class classifies
    URLs as either malicious or benign to safeguard users from potential threats.
    """

    def __init__(self, threshold=0.75, use_onnx: bool = False):
        """
        Initializes an instance of the MaliciousURLs class.

        Parameters:
            threshold (float): The threshold used to determine if the website is malicious. Defaults to 0.75.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._threshold = threshold
        self._classifier = pipeline_text_classification(
            model=_model_path,
            truncation=True,
            padding=True,
            use_onnx=use_onnx,
        )

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        return url_pattern.findall(text)

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        urls = self.extract_urls(output)
        if len(urls) == 0:
            return output, True, 0.0

        logger.debug(f"Found {len(urls)} URLs in the output")

        urls_str = ", ".join(urls)
        result = self._classifier(urls_str)
        malware_score = (
            result[0]["score"] if result[0]["label"] == "MALWARE" else 1 - result[0]["score"]
        )
        if malware_score > self._threshold:
            logger.warning(
                f"Detected malware URL with score: {malware_score}, threshold: {self._threshold}"
            )

            return output, False, round(malware_score, 2)

        logger.debug(
            f"Not malware URLs in the output. Max score: {malware_score}, threshold: {self._threshold}"
        )

        return output, True, 0.0
