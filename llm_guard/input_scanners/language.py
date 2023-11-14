from typing import List

from llm_guard.transformers_helpers import pipeline_text_classification
from llm_guard.util import calculate_risk_score, logger

from .base import Scanner

model_path = (
    "papluca/xlm-roberta-base-language-detection",
    "laiyer/xlm-roberta-base-language-detection-onnx",
)


class Language(Scanner):
    """
    A Scanner subclass responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.
    """

    def __init__(
        self,
        valid_languages: List[str],
        threshold: float = 0.6,
        use_onnx: bool = False,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            valid_languages (List[str]): A list of valid language codes in ISO 639-1.
            threshold (float): Minimum confidence score
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
        """

        self._threshold = threshold
        self._valid_languages = valid_languages
        self._pipeline = pipeline_text_classification(
            model=model_path[0],
            onnx_model=model_path[1],
            top_k=None,
            use_onnx=use_onnx,
            truncation=True,
            max_length=512,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        results = self._pipeline(prompt)
        for result in results[0]:
            if result["label"] in self._valid_languages:
                if result["score"] > self._threshold:
                    logger.debug(
                        f"Language {result['label']} is found in the text with confidence: {result['score']}"
                    )

                    return prompt, True, 0.0

                if result["score"] > highest_score:
                    highest_score = result["score"]

                logger.warning(
                    f"Language {result['label']} is found but confidence is too low: {result['score']}"
                )

        return prompt, False, calculate_risk_score(highest_score, self._threshold)
