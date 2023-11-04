from llm_guard.util import device, is_onnx_supported, lazy_load_dep, logger

from .base import Scanner

_model_path = "martin-ha/toxic-comment-model"


class Toxicity(Scanner):
    """
    A toxicity scanner that uses a pretrained Hugging Face model to assess the toxicity of a given text.

    The class uses a binary toxicity classifier. A score is calculated based on the model's prediction. If the predicted
    label is 'toxic', the score is the model's confidence score. If the predicted label is 'not toxic', the score is
    1 minus the model's confidence score.

    If the toxicity score is less than a predefined threshold, the text is considered non-toxic. Otherwise, it is
    considered toxic.
    """

    def __init__(self, threshold: float = 0.7, use_onnx: bool = False):
        """
        Initializes Toxicity with a threshold for toxicity.

        Parameters:
           threshold (float): Threshold for toxicity. Default is 0.7.
           use_onnx (bool): Whether to use ONNX for inference. Default is False.

        Raises:
           None.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        tokenizer = transformers.AutoTokenizer.from_pretrained(_model_path)

        if use_onnx and is_onnx_supported():
            optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
            model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
                _model_path, export=True
            )
            logger.debug(f"Initialized ONNX model {_model_path} on device {device()}")
        else:
            model = transformers.AutoModelForSequenceClassification.from_pretrained(_model_path)
            logger.debug(f"Initialized model {_model_path} on device {device()}")

        self._text_classification_pipeline = transformers.TextClassificationPipeline(
            model=model,
            tokenizer=tokenizer,
            device=device(),
            truncation=True,
            padding=True,
            max_length=tokenizer.model_max_length,
            batch_size=1,
        )

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        result = self._text_classification_pipeline(prompt)

        toxicity_score = (
            result[0]["score"] if result[0]["label"] == "toxic" else 1 - result[0]["score"]
        )
        if toxicity_score > self._threshold:
            logger.warning(
                f"Detected toxic prompt with score: {toxicity_score}, threshold: {self._threshold}"
            )

            return prompt, False, round(toxicity_score, 2)

        logger.debug(
            f"Not toxicity in the prompt. Max score: {toxicity_score}, threshold: {self._threshold}"
        )

        return prompt, True, 0.0
