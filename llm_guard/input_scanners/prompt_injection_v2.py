from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

_model_path = "hubert233/GPTFuzz"


class PromptInjectionV2(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.

    This dataset is more up-to-date than the popular one.
    However, it performs slower because based on RoBERTa-large model.
    """

    def __init__(self, threshold: float = 0.5):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            threshold (float): Threshold for the injection score. Default is 0.75.

        Raises:
            None.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._text_classification_pipeline = transformers.pipeline(
            "text-classification",
            model=_model_path,
            device=device(),
        )
        logger.debug(f"Initialized model {_model_path} on device {device()}")

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        result = self._text_classification_pipeline(prompt)
        injection_score = round(
            result[0]["score"] if result[0]["label"] == 1 else 1 - result[0]["score"], 2
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
