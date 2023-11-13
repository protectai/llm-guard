from llm_guard.input_scanners.ban_topics import MODEL_LARGE
from llm_guard.transformers_helpers import pipeline_zero_shot_classification
from llm_guard.util import logger

from .base import Scanner

_model = MODEL_LARGE
_categories = ["refusal", "not_refusal"]


class NoRefusal(Scanner):
    """
    A class used to detect and handle refusals in language model output.

    This class uses the zero-shot-classification model from Hugging Face to classify refusals.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(self, threshold: float = 0.5, use_onnx: bool = False):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            threshold (float): The similarity threshold to consider an output as refusal.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._threshold = threshold

        self._classifier = pipeline_zero_shot_classification(
            model=_model["path"],
            onnx_model=_model["onnx_path"],
            use_onnx=use_onnx,
            max_length=_model["max_length"],
            truncation=True,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        output_model = self._classifier(output, _categories, multi_label=True)
        combined_output = dict(zip(output_model["labels"], output_model["scores"]))

        max_score = round(combined_output["refusal"], 2)
        if max_score > self._threshold:
            logger.warning(f"Refusal detected for the prompt: {combined_output}")

            return output, False, max_score

        logger.debug(f"No refusal detected: {combined_output}")

        return output, True, 0.0
