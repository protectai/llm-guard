import logging

from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, pipeline

from llm_guard.util import device_int as device

from .base import Scanner

log = logging.getLogger(__name__)
_model_path = "d4data/bias-detection-model"


class Bias(Scanner):
    """
    This class is designed to detect and evaluate potential biases in text using a pretrained model from HuggingFace.
    """

    def __init__(self, threshold: float = 0.75):
        """
        Initializes the Bias scanner with a probability threshold for bias detection.

        Parameters:
           threshold (float): The threshold above which a text is considered biased.
                              Default is 0.75.
        """
        self._threshold = threshold

        tokenizer = AutoTokenizer.from_pretrained(_model_path)
        model = TFAutoModelForSequenceClassification.from_pretrained(_model_path)

        self._classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device,
        )
        log.debug(f"Initialized model {_model_path} on device {device}")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        classifier_output = self._classifier(output)

        score = (
            classifier_output[0]["score"]
            if classifier_output[0]["label"] == "Biased"
            else 1 - classifier_output[0]["score"]
        )
        if score > self._threshold:
            log.warning(f"Detected biased text with score: {score}, threshold: {self._threshold}")

            return output, False, round(score, 2)

        log.debug(f"Not biased result. Max score: {score}, threshold: {self._threshold}")

        return output, True, 0.0
