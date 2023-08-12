import logging
import os

from sentence_transformers import SentenceTransformer, util

from llm_guard.util import read_json_file

from .base import Scanner

log = logging.getLogger(__name__)
_dataset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "resources", "refusal.json"
)
_transformer_name = "sentence-transformers/all-MiniLM-L6-v2"


class NoRefusal(Scanner):
    """
    A class used to detect and handle refusals in language model output.

    This class uses a transformer model to encode the output and compare it to a dataset of refusal
    sentences to identify any refusals.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(self, dataset_path: str = _dataset_path, threshold: float = 0.5):
        """
        Initializes an instance of the NoRefusal class.

        Parameters:
            dataset_path (str): The path to the refusal dataset. Default is refusal.json.
            threshold (float): The similarity threshold to consider an output as refusal.
        """

        self._threshold = threshold
        self._transformer_model = SentenceTransformer(_transformer_name)
        self._dataset_embeddings = [
            self._transformer_model.encode(s, convert_to_tensor=True)
            for s in read_json_file(dataset_path)["refusal"]
        ]

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        similarities = []
        text_embedding = self._transformer_model.encode(output, convert_to_tensor=True)
        for embedding in self._dataset_embeddings:
            similarity = util.pytorch_cos_sim(text_embedding, embedding)
            similarities.append(similarity.item())

        max_score = round(max(similarities) if similarities else 0, 2)
        if max_score > self._threshold:
            log.warning(f"Detected refusal result with similarity score: {max_score}")
            return output, False, max_score

        log.debug(f"No refusals. Max similarity with the known refusal results: {max_score}")
        return output, True, 0.0
