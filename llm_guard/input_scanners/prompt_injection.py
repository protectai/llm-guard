from typing import List, Optional

from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

MODEL_JASPERLS = "JasperLS/deberta-v3-base-injection"
MODEL_GPTFUZZ = "hubert233/GPTFuzz"  # This dataset is more up-to-date than the popular one. However, it performs slower because based on RoBERTa-large model.

all_models = [
    MODEL_JASPERLS,
    MODEL_GPTFUZZ,
]

_labels_mapping = {
    MODEL_JASPERLS: "INJECTION",
    MODEL_GPTFUZZ: 1,
}


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.

    Note: The current model has been known to yield high false positive rates and might not be suited for production use.
    """

    def __init__(self, models: Optional[List[str]] = None, threshold: float = 0.5):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            models (List[str], optional): Chosen models to classify prompt. Default is JasperLS and GPTFuzz.
            threshold (float): Threshold for the injection score. Default is 0.75.

        Raises:
            ValueError: If non-existent models were provided.
        """

        self._threshold = threshold

        if models is None:
            models = [MODEL_JASPERLS, MODEL_GPTFUZZ]

        if not set(models).issubset(set(all_models)):
            raise ValueError(f"Models must be in the list of allowed: {all_models}")

        logger.debug(f"Prompt injection models: {models}")

        transformers = lazy_load_dep("transformers")

        pipelines = {}
        for model_path in models:
            model = transformers.AutoModelForSequenceClassification.from_pretrained(model_path)
            tokenizer = transformers.AutoTokenizer.from_pretrained(model_path)

            pipelines[model_path] = transformers.TextClassificationPipeline(
                model=model,
                tokenizer=tokenizer,
                device=device(),
            )

            logger.debug(f"Initialized model {model_path} on device {device()}")

        self._text_classification_pipelines = pipelines

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        for model_path in self._text_classification_pipelines:
            result = self._text_classification_pipelines[model_path](prompt)
            model_label = _labels_mapping[model_path]

            injection_score = round(
                result[0]["score"] if result[0]["label"] == model_label else 1 - result[0]["score"],
                2,
            )

            if injection_score > self._threshold:
                logger.warning(
                    f"Detected prompt injection using {model_path} with score: {injection_score}"
                )

                return prompt, False, injection_score

            logger.debug(
                f"No prompt injection detected using {model_path}, score: {injection_score}"
            )

        return prompt, True, 0.0
