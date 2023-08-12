import logging
import os

from sentence_transformers import SentenceTransformer, util

from llm_guard.util import read_json_file

from .base import Scanner

log = logging.getLogger(__name__)
_dataset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "resources", "jailbreak.json"
)
_transformer_name = "sentence-transformers/all-MiniLM-L6-v2"


class Jailbreak(Scanner):
    """
    A language scanner based on the sentence-transformer model. It is used to detect if a prompt
    tries to perform a jailbreak attack using internal dataset and sentence transformer for similarity measures.
    """

    def __init__(self, dataset_path: str = _dataset_path, threshold: float = 0.6):
        """
        Initializes Jailbreak with a dataset and a similarity threshold.

        Parameters:
            dataset_path (str): Path to the dataset with known jailbreak attempts. Default is the pre-set path 'jaulbreak.json'.
            threshold (float): Threshold for similarity measure. Default is 0.6.

        Raises:
            None.
        """
        self._threshold = threshold
        self._transformer_model = SentenceTransformer(_transformer_name)
        self._dataset_embeddings = [
            self._transformer_model.encode(s, convert_to_tensor=True)
            for s in read_json_file(dataset_path)["jailbreak"]
        ]

    def scan(self, prompt: str) -> (str, bool, float):
        similarities = []
        text_embedding = self._transformer_model.encode(prompt, convert_to_tensor=True)
        for embedding in self._dataset_embeddings:
            similarity = util.pytorch_cos_sim(text_embedding, embedding)
            similarities.append(similarity.item())

        max_score = round(max(similarities) if similarities else 0, 2)
        if max_score > self._threshold:
            log.warning(f"Detected jailbreak prompt with similarity score: {max_score}")

            return prompt, False, max_score

        log.debug(f"No jailbreaks. Max similarity with the known jailbreak prompts: {max_score}")
        return prompt, True, max_score
