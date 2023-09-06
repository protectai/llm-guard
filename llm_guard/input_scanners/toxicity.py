import logging

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TextClassificationPipeline,
)

from llm_guard.util import device

from .base import Scanner

_model_path = "martin-ha/toxic-comment-model"

log = logging.getLogger(__name__)


class Toxicity(Scanner):
    """
    A toxicity scanner that uses a pretrained Hugging Face model to assess the toxicity of a given text.

    The class uses a binary toxicity classifier. A score is calculated based on the model's prediction. If the predicted
    label is 'toxic', the score is the model's confidence score. If the predicted label is 'not toxic', the score is
    1 minus the model's confidence score.

    If the toxicity score is less than a predefined threshold, the text is considered non-toxic. Otherwise, it is
    considered toxic.
    """

    def __init__(self, threshold: float = 0.7):
        """
        Initializes Toxicity with a threshold for toxicity.

        Parameters:
           threshold (float): Threshold for toxicity. Default is 0.7.

        Raises:
           None.
        """

        model = AutoModelForSequenceClassification.from_pretrained(_model_path)
        self._tokenizer = AutoTokenizer.from_pretrained(_model_path)
        self._threshold = threshold
        self._text_classification_pipeline = TextClassificationPipeline(
            model=model,
            tokenizer=self._tokenizer,
            device=device,
        )
        log.debug(f"Initialized model {_model_path} on device {device}")

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        result = self._text_classification_pipeline(
            prompt, truncation=True, padding=True, max_length=self._tokenizer.model_max_length
        )

        toxicity_score = (
            result[0]["score"] if result[0]["label"] == "toxic" else 1 - result[0]["score"]
        )
        if toxicity_score > self._threshold:
            log.warning(
                f"Detected toxic prompt with score: {toxicity_score}, threshold: {self._threshold}"
            )

            return prompt, False, round(toxicity_score, 2)

        log.debug(
            f"Not toxicity in the prompt. Max score: {toxicity_score}, threshold: {self._threshold}"
        )

        return prompt, True, 0.0
