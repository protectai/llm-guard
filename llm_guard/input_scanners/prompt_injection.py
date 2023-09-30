from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

_model_path = "JasperLS/deberta-v3-base-injection"


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.

    Note: The current model has been known to yield high false positive rates and might not be suited for production use.
    """

    def __init__(self, threshold: float = 0.75):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            threshold (float): Threshold for the injection score. Default is 0.75.

        Raises:
            None.
        """

        transformers = lazy_load_dep("transformers")
        model = transformers.AutoModelForSequenceClassification.from_pretrained(_model_path)
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(_model_path)
        self._threshold = threshold
        self._text_classification_pipeline = transformers.TextClassificationPipeline(
            model=model,
            tokenizer=self._tokenizer,
            device=device(),
        )
        logger.debug(f"Initialized model {_model_path} on device {device()}")

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        result = self._text_classification_pipeline(prompt)
        injection_score = round(
            result[0]["score"] if result[0]["label"] == "INJECTION" else 1 - result[0]["score"], 2
        )

        if injection_score > self._threshold:
            logger.warning(
                f"Detected prompt injection with score: {injection_score}, threshold: {self._threshold}"
            )

            return prompt, False, injection_score

        logger.debug(
            f"No prompt injection detected (max score: {injection_score}, threshold: {self._threshold})"
        )

        return prompt, True, 0.0
