from typing import Optional

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import calculate_risk_score, get_logger

from .base import Scanner

LOGGER = get_logger()

MODEL_SM = Model(
    path="vishnun/codenlbert-sm",
    revision="2caf5a621b29c50038ee081479a82f192e9a5e69",
    onnx_path="",
    onnx_revision="",
    pipeline_kwargs={"truncation": True},
)

MODEL_TINY = Model(
    path="vishnun/codenlbert-tiny",
    revision="2caf5a621b29c50038ee081479a82f192e9a5e69",
    onnx_path="",
    onnx_revision="",
    pipeline_kwargs={"truncation": True},
)


class BanCode(Scanner):
    """
    A scanner that detects if input is code and blocks it.
    """

    def __init__(
        self,
        *,
        model: Optional[Model] = None,
        threshold: float = 0.9,
        use_onnx: bool = False,
    ):
        """
        Initializes the BanCode scanner.

        Parameters:
           model (Model, optional): The model object.
           threshold (float): The probability threshold. Default is 0.9.
           use_onnx (bool): Whether to use ONNX instead of PyTorch for inference.
        """

        self._threshold = threshold
        if model is None:
            model = MODEL_SM

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )

        self._classifier = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **model.pipeline_kwargs,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        highest_score = 0.0
        result = self._classifier(prompt)[0]
        score = round(
            1 - result["score"] if result["label"] == "clean" else result["score"],
            2,
        )

        if score > highest_score:
            highest_score = score

        if score > self._threshold:
            LOGGER.warning("Detected gibberish text", score=score, threshold=self._threshold)

            return prompt, False, calculate_risk_score(score, self._threshold)

            LOGGER.debug(
                "No gibberish in the text", highest_score=highest_score, threshold=self._threshold
            )

        return prompt, True, 0.0
