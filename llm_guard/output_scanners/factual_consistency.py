from __future__ import annotations

from typing import TYPE_CHECKING

from llm_guard.input_scanners.ban_topics import MODEL_DEBERTA_BASE_V2
from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification
from llm_guard.util import device, get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()

if TYPE_CHECKING:
    import torch

torch = lazy_load_dep("torch")


class FactualConsistency(Scanner):
    """
    FactualConsistency Class:

    This class checks for entailment between a given prompt and output using a pretrained NLI model.
    """

    def __init__(
        self,
        *,
        model: Model | None = None,
        minimum_score=0.75,
        use_onnx=False,
    ) -> None:
        """
        Initializes an instance of the Refutation class.

        Parameters:
            model (Model, optional): The model to use for entailment checking. Defaults to None.
            minimum_score (float): The minimum entailment score for the output to be considered valid. Defaults to 0.75.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._minimum_score = minimum_score

        if model is None:
            model = MODEL_DEBERTA_BASE_V2

        self._tokenizer, self._model = get_tokenizer_and_model_for_classification(
            model=model,
            use_onnx=use_onnx,
        )
        self._model = self._model.to(device())
        if not use_onnx:
            self._model.eval()

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if prompt.strip() == "":
            return output, True, 0.0

        tokenized_input_seq_pair = self._tokenizer(
            output, prompt, padding=True, truncation=True, return_tensors="pt"
        )
        tokenized_input_seq_pair = {
            key: val.to(device()) for key, val in tokenized_input_seq_pair.items()
        }

        with torch.no_grad():
            model_output = self._model(**tokenized_input_seq_pair)
            model_prediction = torch.softmax(model_output["logits"][0], -1).tolist()

        label_names = ["entailment", "not_entailment"]
        prediction = {
            name: round(float(pred), 2) for pred, name in zip(model_prediction, label_names)
        }

        entailment_score = prediction["entailment"]
        if entailment_score < self._minimum_score:
            LOGGER.warning("Entailment score is below the threshold", prediction=prediction)

            return output, False, prediction["not_entailment"]

        LOGGER.debug("The output is factually consistent", prediction=prediction)

        return output, True, 0.0
