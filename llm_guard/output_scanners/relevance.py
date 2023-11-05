from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

MODEL_EN_BGE_BASE = "BAAI/bge-base-en-v1.5"
MODEL_EN_BGE_LARGE = "BAAI/bge-large-en-v1.5"
MODEL_EN_BGE_SMALL = "BAAI/bge-small-en-v1.5"

all_models = [MODEL_EN_BGE_LARGE, MODEL_EN_BGE_BASE, MODEL_EN_BGE_SMALL]


class Relevance(Scanner):
    """
    A class used to scan the relevance of the output of a language model to the input prompt.

    This class uses SentenceTransformers to encode the prompt and output into vector embeddings, then computes
    the cosine similarity between them. If the similarity is below a given threshold, the output is considered
    not relevant to the prompt.
    """

    def __init__(self, threshold: float = 0.5, model: str = MODEL_EN_BGE_BASE):
        """
        Initializes an instance of the Relevance class.

        Parameters:
            threshold (float): The minimum similarity score to compare prompt and output.
            model (str): Model for calculating embeddings. Default is `BAAI/bge-base-en-v1.5`.
        """

        self._threshold = threshold

        if model not in all_models:
            raise ValueError("This model is not supported")

        fe = lazy_load_dep("FlagEmbedding")

        use_fp16 = True
        if str(device()) == "mps":
            use_fp16 = False

        self._model = fe.FlagModel(
            model,
            query_instruction_for_retrieval=None,
            use_fp16=use_fp16,
        )

        logger.debug(f"Initialized model {model} on device {device()}")

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        prompt_embedding = self._model.encode(prompt)
        output_embedding = self._model.encode(output)
        similarity = prompt_embedding @ output_embedding.T

        if similarity < self._threshold:
            logger.warning(f"Result is not similar to the prompt. Similarity score: {similarity}")

            return output, False, round(1 - similarity, 2)

        logger.debug(f"Result is similar to the prompt. Similarity score: {similarity}")

        return output, True, 0.0
