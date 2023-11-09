from typing import Dict, List, Optional

from llm_guard.transformers_helpers import pipeline_text_classification
from llm_guard.util import logger

from .base import Scanner

# This model has been known to yield high false positive rates and might not be suited for production use.
MODEL_DEEPSET = {
    "path": "deepset/deberta-v3-base-injection",
    "label": "INJECTION",
    "max_length": 512,
    "onnx_supported": False,  # Deberta is not supported by ONNX
}

# This dataset is more up-to-date. However, it performs slower because based on RoBERTa-large model.
MODEL_GPTFUZZ = {
    "path": "hubert233/GPTFuzz",
    "label": 1,
    "max_length": 512,
    "onnx_supported": True,
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

    def __init__(
        self, models: Optional[List[Dict]] = None, threshold: float = 0.5, use_onnx: bool = False
    ):
        """
        Initializes PromptInjection with a threshold.

        Parameters:
            models (List[Dict], optional): Chosen models to classify prompt. Default is JasperLS.
            threshold (float): Threshold for the injection score. Default is 0.75.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.

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

        pipelines = {}
        for model in models:
            try:
                pipelines[model["path"]] = pipeline_text_classification(
                    model=model["path"],
                    use_onnx=use_onnx and model["onnx_supported"],
                    truncation=True,
                    max_length=model["max_length"],
                )
            except Exception as err:
                logger.error(f"Failed to load model: {err}")

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
