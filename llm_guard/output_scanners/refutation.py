from llm_guard.input_scanners.ban_topics import MODEL_BASE
from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

torch = lazy_load_dep("torch")

_model_path = MODEL_BASE


class Refutation(Scanner):
    """
    Refutation Class:

    This class checks for refutation between a given prompt and output using a pretrained NLI model.
    """

    def __init__(self, threshold=0.5):
        """
        Initializes an instance of the Refutation class.

        Parameters:
            threshold (float): The threshold used to determine refutation. Defaults to 0.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(_model_path)
        self._model = transformers.AutoModelForSequenceClassification.from_pretrained(
            _model_path
        ).to(device())

        logger.debug(f"Initialized sentence transformer {_model_path} on device {device()}")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        tokenized_input_seq_pair = self._tokenizer(
            output, prompt, truncation=True, return_tensors="pt"
        ).to(device())
        model_output = self._model(tokenized_input_seq_pair["input_ids"])
        model_prediction = torch.softmax(model_output["logits"][0], -1).tolist()
        label_names = ["entailment", "not_entailment"]
        prediction = {
            name: round(float(pred), 2) for pred, name in zip(model_prediction, label_names)
        }

        not_entailment_score = prediction["not_entailment"]
        if not_entailment_score > self._threshold:
            logger.warning(f"Detected refutation in the output: {prediction}")

            return output, False, not_entailment_score

        logger.debug(f"Not refutation in the output: {prediction}")

        return output, True, 0.0
