from llm_guard.input_scanners.ban_topics import MODEL_LARGE
from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

_model_path = MODEL_LARGE
_categories = ["refusal", "not_refusal"]


class NoRefusal(Scanner):
    """
    A class used to detect and handle refusals in language model output.

    This class uses the zero-shot-classification model from Hugging Face to classify refusals.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            threshold (float): The similarity threshold to consider an output as refusal.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._classifier = transformers.pipeline(
            "zero-shot-classification",
            model=_model_path,
            device=device(),
            truncation=True,
            max_length=512,
        )
        logger.debug(f"Initialized model {_model_path} on device {device()}")

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
