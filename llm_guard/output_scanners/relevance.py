from typing import Tuple

from llm_guard.transformers_helpers import get_tokenizer, is_onnx_supported
from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

MODEL_EN_BGE_BASE = (
    "BAAI/bge-base-en-v1.5",
    "zeroshot/bge-base-en-v1.5-quant",  # Quantized and converted to ONNX version of BGE base
)
MODEL_EN_BGE_LARGE = (
    "BAAI/bge-large-en-v1.5",
    "zeroshot/bge-large-en-v1.5-quant",  # Quantized and converted to ONNX version of BGE large
)
MODEL_EN_BGE_SMALL = (
    "BAAI/bge-small-en-v1.5",
    "zeroshot/bge-small-en-v1.5-quant",  # Quantized and converted to ONNX version of BGE small
)

all_models = [MODEL_EN_BGE_LARGE, MODEL_EN_BGE_BASE, MODEL_EN_BGE_SMALL]

torch = lazy_load_dep("torch")
np = lazy_load_dep("numpy")


class Relevance(Scanner):
    """
    A class used to scan the relevance of the output of a language model to the input prompt.

    This class uses SentenceTransformers to encode the prompt and output into vector embeddings, then computes
    the cosine similarity between them. If the similarity is below a given threshold, the output is considered
    not relevant to the prompt.
    """

    def __init__(
        self, threshold: float = 0.5, model: Tuple = MODEL_EN_BGE_BASE, use_onnx: bool = False
    ):
        """
        Initializes an instance of the Relevance class.

        Parameters:
            threshold (float): The minimum similarity score to compare prompt and output.
            model (Tuple): Model for calculating embeddings. Default is `BAAI/bge-base-en-v1.5`.
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """

        self._threshold = threshold

        if model not in all_models:
            raise ValueError("This model is not supported")
        model_path = model[0]

        self.pooling_method = "cls"
        self.normalize_embeddings = True

        if use_onnx and is_onnx_supported() is False:
            logger.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
            use_onnx = False

        if use_onnx:
            model_path = model[1]
            optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
            self._model = optimum_onnxruntime.ORTModelForFeatureExtraction.from_pretrained(
                model_path,
                export=False,
            )
            logger.debug(f"Initialized ONNX model {model_path} on device {device()}")
        else:
            transformers = lazy_load_dep("transformers")
            self._model = transformers.AutoModel.from_pretrained(model_path).to(device())
            logger.debug(f"Initialized model {model_path} on device {device()}")
            self._model.eval()

        self._tokenizer = get_tokenizer(model_path)

    def pooling(self, last_hidden_state: torch.Tensor, attention_mask: torch.Tensor = None):
        if self.pooling_method == "cls":
            return last_hidden_state[:, 0]
        elif self.pooling_method == "mean":
            s = torch.sum(last_hidden_state * attention_mask.unsqueeze(-1).float(), dim=1)
            d = attention_mask.sum(dim=1, keepdim=True).float()
            return s / d

    @torch.no_grad()
    def _encode(self, sentence: str, max_length: int = 512) -> np.ndarray:
        inputs = self._tokenizer(
            [sentence],
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length,
        ).to(device())
        last_hidden_state = self._model(**inputs, return_dict=True).last_hidden_state
        embeddings = self.pooling(last_hidden_state, inputs["attention_mask"])
        if self.normalize_embeddings:
            embeddings = torch.nn.functional.normalize(embeddings, dim=-1)
        embeddings = embeddings.cpu().numpy()

        return embeddings[0]

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        prompt_embedding = self._encode(prompt)
        output_embedding = self._encode(output)
        similarity = prompt_embedding @ output_embedding.T

        if similarity < self._threshold:
            logger.warning(f"Result is not similar to the prompt. Similarity score: {similarity}")

            return output, False, round(1 - similarity, 2)

        logger.debug(f"Result is similar to the prompt. Similarity score: {similarity}")

        return output, True, 0.0
