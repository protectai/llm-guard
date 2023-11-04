from typing import Dict, List, Optional

from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

# This model has been known to yield high false positive rates and might not be suited for production use.
MODEL_DEEPSET = {
    "path": "deepset/deberta-v3-base-injection",
    "label": "INJECTION",
    "max_length": 512,
}

# This dataset is more up-to-date. However, it performs slower because based on RoBERTa-large model.
MODEL_GPTFUZZ = {
    "path": "hubert233/GPTFuzz",
    "label": 1,
    "max_length": 512,
}

ALL_MODELS = [
    MODEL_DEEPSET,
    MODEL_GPTFUZZ,
]


class PromptInjection(Scanner):
    """
    A prompt injection scanner based on HuggingFace model. It is used to
    detect if a prompt is attempting to perform an injection attack.
    """

    def __init__(self, models: Optional[List[Dict]] = None, threshold: float = 0.5):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            models (List[Dict], optional): Chosen models to classify prompt. Default is JasperLS.
            threshold (float): Threshold for the injection score. Default is 0.75.

        Raises:
            ValueError: If non-existent models were provided.
        """

        self._threshold = threshold

        if models is None:
            models = [MODEL_DEEPSET]

        for model in models:
            if model not in ALL_MODELS:
                raise ValueError(f"Models must be in the list of allowed: {ALL_MODELS}")

        logger.debug(f"Prompt injection models: {models}")

        transformers = lazy_load_dep("transformers")

        pipelines = {}
        for model in models:
            try:
                tf_tokenizer = transformers.AutoTokenizer.from_pretrained(model["path"])
                tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(
                    model["path"]
                )

                pipelines[model["path"]] = transformers.pipeline(
                    "text-classification",
                    model=tf_model,
                    tokenizer=tf_tokenizer,
                    truncation=True,
                    max_length=model["max_length"],
                    batch_size=1,
                    device=device(),
                )
            except Exception as err:
                logger.error(f"Failed to load model: {err}")

            logger.debug(f"Initialized model {model['path']} on device {device()}")

        self._text_classification_pipelines = pipelines

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        for model_path in self._text_classification_pipelines:
            try:
                result = self._text_classification_pipelines[model_path](prompt)
            except Exception as err:
                logger.error(f"Failed to get output of the model: {err}")
                return prompt, True, 0.0

            model_label = ALL_MODELS[[m["path"] for m in ALL_MODELS].index(model_path)]["label"]

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
