from llm_guard.transformers_helpers import pipeline_text_classification
from llm_guard.util import logger

from .base import Scanner

_model_path = (
    "valurank/distilroberta-bias",
    "laiyer/distilroberta-bias-onnx",  # ONNX model
)


class Bias(Scanner):
    """
    This class is designed to detect and evaluate potential biases in text using a pretrained model from HuggingFace.
    """

    def __init__(self, threshold: float = 0.75, use_onnx: bool = False):
        """
        Initializes the Bias scanner with a probability threshold for bias detection.

        Parameters:
           threshold (float): The threshold above which a text is considered biased.
                              Default is 0.75.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
        """
        self._threshold = threshold

        self._classifier = pipeline_text_classification(
            model=_model_path[0],
            onnx_model=_model_path[1],
            truncation=True,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        classifier_output = self._classifier(output)
        score = round(
            classifier_output[0]["score"]
            if classifier_output[0]["label"] == "BIASED"
            else 1 - classifier_output[0]["score"],
            2,
        )
        if score > self._threshold:
            logger.warning(
                f"Detected biased text with score: {score}, threshold: {self._threshold}"
            )

            return output, False, score

        logger.debug(f"Not biased result. Max score: {score}, threshold: {self._threshold}")

        return output, True, 0.0
