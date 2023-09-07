import logging
import math

from transformers import AutoModelForSequenceClassification, AutoTokenizer

from llm_guard.util import device

from .base import Scanner

_model_path = "nicholasKluge/ToxicityModel"

log = logging.getLogger(__name__)


class Toxicity(Scanner):
    """
    A class used to detect toxicity in the output of a language model.

    This class uses a pre-trained toxicity model from HuggingFace to calculate a toxicity score (from -1 to 1) for the output.
    A negative value (closer to 0 as the label output) indicates toxicity in the text, while a positive logit
    (closer to 1 as the label output) suggests non-toxicity.
    The score is then compared to a predefined threshold. If the score exceeds the threshold, the output is
    deemed toxic.
    """

    def __init__(self, threshold=0):
        """
        Initializes an instance of the Toxicity class.

        Parameters:
            threshold (float): The threshold used to determine toxicity. Defaults to 0.
        """

        self._model = AutoModelForSequenceClassification.from_pretrained(_model_path)
        self._model.eval()
        self._model.to(device)
        self._tokenizer = AutoTokenizer.from_pretrained(_model_path)
        self._threshold = threshold

        log.debug(f"Initialized model {_model_path} on device {device}")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        tokens = self._tokenizer(
            prompt,
            output,
            truncation=True,
            max_length=512,
            return_token_type_ids=False,
            return_tensors="pt",
            return_attention_mask=True,
        ).to(device)
        toxicity_score = self._model(**tokens)[0].item()
        risk_score = round(1 / (1 + math.exp(toxicity_score)), 2)
        if toxicity_score > self._threshold:
            log.debug(
                f"Not toxicity in the output. Max score: {toxicity_score}, threshold: {self._threshold}"
            )

            return output, True, 0.0

        log.warning(
            f"Detected toxic in the output with score: {toxicity_score}, threshold: {self._threshold}"
        )

        return output, False, risk_score
