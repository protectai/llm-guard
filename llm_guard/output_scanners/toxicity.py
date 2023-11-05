import math

from llm_guard.transformers_helpers import is_onnx_supported
from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

_model_path = "nicholasKluge/ToxicityModel"


class Toxicity(Scanner):
    """
    A class used to detect toxicity in the output of a language model.

    This class uses a pre-trained toxicity model from HuggingFace to calculate a toxicity score (from -1 to 1) for the output.
    A negative value (closer to 0 as the label output) indicates toxicity in the text, while a positive logit
    (closer to 1 as the label output) suggests non-toxicity.
    The score is then compared to a predefined threshold. If the score exceeds the threshold, the output is
    deemed toxic.
    """

    def __init__(self, threshold=0, use_onnx: bool = False):
        """
        Initializes an instance of the Toxicity class.

        Parameters:
            threshold (float): The threshold used to determine toxicity. Defaults to 0.
            use_onnx (bool): Whether to use ONNX for inference. Defaults to False.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(_model_path)

        if use_onnx and is_onnx_supported() is False:
            logger.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
            use_onnx = False

        if use_onnx:
            optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
            self._model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
                _model_path, export=True
            )
            logger.debug(f"Initialized ONNX model {_model_path} on device {device()}")
        else:
            self._model = transformers.AutoModelForSequenceClassification.from_pretrained(
                _model_path
            )
            self._model.eval()
            logger.debug(f"Initialized model {_model_path} on device {device()}")

        self._model.to(device())

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "":
            return output, True, 0.0

        tokens = self._tokenizer(
            prompt,
            output,
            truncation=True,
            max_length=self._tokenizer.model_max_length,
            return_token_type_ids=False,
            return_tensors="pt",
            return_attention_mask=True,
        ).to(device())
        toxicity_score = self._model(**tokens)[0].item()
        risk_score = round(1 / (1 + math.exp(toxicity_score)), 2)
        if toxicity_score > self._threshold:
            logger.debug(
                f"Not toxicity in the output. Max score: {toxicity_score}, threshold: {self._threshold}"
            )

            return output, True, 0.0

        logger.warning(
            f"Detected toxic in the output with score: {toxicity_score}, threshold: {self._threshold}"
        )

        return output, False, risk_score
