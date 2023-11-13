from llm_guard.input_scanners.ban_topics import MODEL_BASE
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification
from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

torch = lazy_load_dep("torch")

_model = MODEL_BASE


class FactualConsistency(Scanner):
    """
    FactualConsistency Class:

    This class checks for entailment between a given prompt and output using a pretrained NLI model.
    """

    def __init__(self, minimum_score=0.5, use_onnx=False):
        """
        Initializes an instance of the Refutation class.

        Parameters:
            minimum_score (float): The minimum entailment score for the output to be considered valid. Defaults to 0.5.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._minimum_score = minimum_score

        self._tokenizer, self._model = get_tokenizer_and_model_for_classification(
            model=_model["path"],
            onnx_model=_model["onnx_path"],
            use_onnx=use_onnx,
        )
        self._model = self._model.to(device())

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        tokenized_input_seq_pair = self._tokenizer(
            output, prompt, padding=True, truncation=True, return_tensors="pt"
        ).to(device())

        model_output = self._model(
            tokenized_input_seq_pair["input_ids"], tokenized_input_seq_pair["attention_mask"]
        )
        model_prediction = torch.softmax(model_output["logits"][0], -1).tolist()
        label_names = ["entailment", "not_entailment"]
        prediction = {
            name: round(float(pred), 2) for pred, name in zip(model_prediction, label_names)
        }

        entailment_score = prediction["entailment"]
        if entailment_score < self._minimum_score:
            logger.warning(f"Entailment score is below the threshold: {prediction}")

            return output, False, prediction["not_entailment"]

        logger.debug(f"The output is factually consistent: {prediction}")

        return output, True, 0.0
