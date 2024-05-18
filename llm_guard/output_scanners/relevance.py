from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np
import torch

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer, is_onnx_supported
from llm_guard.util import device, get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()

MODEL_EN_BGE_BASE = Model(
    path="BAAI/bge-base-en-v1.5",
    revision="a5beb1e3e68b9ab74eb54cfd186867f64f240e1a",
    onnx_path="BAAI/bge-base-en-v1.5",
    onnx_subfolder="onnx",
    onnx_filename="model.onnx",
    onnx_revision="a5beb1e3e68b9ab74eb54cfd186867f64f240e1a",
)
MODEL_EN_BGE_LARGE = Model(
    path="BAAI/bge-large-en-v1.5",
    revision="d4aa6901d3a41ba39fb536a557fa166f842b0e09",
    onnx_path="BAAI/bge-large-en-v1.5",
    onnx_subfolder="onnx",
    onnx_revision="d4aa6901d3a41ba39fb536a557fa166f842b0e09",
)
MODEL_EN_BGE_SMALL = Model(
    path="BAAI/bge-small-en-v1.5",
    revision="5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
    onnx_path="BAAI/bge-small-en-v1.5",
    onnx_revision="5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
    onnx_subfolder="onnx",
)


if TYPE_CHECKING:
    import optimum.onnxruntime


class Relevance(Scanner):
    """
    A class used to scan the relevance of the output of a language model to the input prompt.

    This class encodes the prompt and output into vector embeddings, then computes
    the cosine similarity between them. If the similarity is below a given threshold, the output is considered
    not relevant to the prompt.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.5,
        model: Model | None = None,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes an instance of the Relevance class.

        Parameters:
            threshold: The minimum similarity score to compare prompt and output.
            model: Model for calculating embeddings. Default is `BAAI/bge-base-en-v1.5`.
            use_onnx: Whether to use the ONNX version of the model. Defaults to False.
        """

        self._threshold = threshold

        if model is None:
            model = MODEL_EN_BGE_BASE

        self.pooling_method = "cls"
        self.normalize_embeddings = True

        if use_onnx and is_onnx_supported() is False:
            LOGGER.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
            use_onnx = False

        if use_onnx:
            optimum_onnxruntime = cast(
                "optimum.onnxruntime",
                lazy_load_dep(
                    "optimum.onnxruntime",
                    "optimum[onnxruntime-gpu]"
                    if device().type == "cuda"
                    else "optimum[onnxruntime]",
                ),
            )
            assert model.onnx_path is not None
            self._model = optimum_onnxruntime.ORTModelForFeatureExtraction.from_pretrained(
                model.onnx_path,
                export=False,
                subfolder=model.onnx_subfolder,
                file_name=model.onnx_filename,
                revision=model.onnx_revision,
                provider=(
                    "CUDAExecutionProvider" if device().type == "cuda" else "CPUExecutionProvider"
                ),
                **model.kwargs,
            )
            LOGGER.debug("Initialized ONNX model", model=model, device=device())
        else:
            transformers = lazy_load_dep("transformers")
            self._model = transformers.AutoModel.from_pretrained(
                model.path, subfolder=model.subfolder, revision=model.revision, **model.kwargs
            ).to(device())
            LOGGER.debug("Initialized model", model=model, device=device())
            self._model.eval()

        self._tokenizer = get_tokenizer(model)

    def pooling(
        self, last_hidden_state: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor | None:
        if self.pooling_method == "cls":
            return last_hidden_state[:, 0]
        elif self.pooling_method == "mean":
            s = torch.sum(last_hidden_state * attention_mask.unsqueeze(-1).float(), dim=1)
            d = attention_mask.sum(dim=1, keepdim=True).float()
            return s / d
        return None

    @torch.no_grad()
    def _encode(self, sentence: str, max_length: int = 512) -> np.ndarray:
        inputs = self._tokenizer(
            [sentence],
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length,
        )
        inputs = {key: val.to(device()) for key, val in inputs.items()}

        with torch.no_grad():
            last_hidden_state = self._model(**inputs, return_dict=True).last_hidden_state
            embeddings = self.pooling(last_hidden_state, inputs["attention_mask"])
            assert embeddings is not None
            if self.normalize_embeddings:
                embeddings = torch.nn.functional.normalize(embeddings, dim=-1)

            embeddings = embeddings.cpu().numpy()

        return embeddings[0]

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        if output.strip() == "":
            return output, True, 0.0

        prompt_embedding = self._encode(prompt)
        output_embedding = self._encode(output)
        similarity = prompt_embedding.dot(output_embedding.T)

        if similarity < self._threshold:
            LOGGER.warning("Result is not similar to the prompt", similarity_score=similarity)

            return output, False, round(1 - similarity, 2)

        LOGGER.debug("Result is similar to the prompt", similarity_score=similarity)

        return output, True, 0.0
