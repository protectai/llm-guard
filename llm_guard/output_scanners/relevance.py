import torch
import torch.nn.functional as F

from llm_guard.util import device, lazy_load_dep, logger

from .base import Scanner

_transformer_name = "sentence-transformers/all-MiniLM-L6-v2"


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask, torch_device):
    token_embeddings = model_output.last_hidden_state.to(
        torch_device
    )  # Move token_embeddings to MPS device
    attention_mask = attention_mask.to(torch_device)  # Move attention_mask to MPS device
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


class Relevance(Scanner):
    """
    A class used to scan the relevance of the output of a language model to the input prompt.

    This class uses SentenceTransformers to encode the prompt and output into vector embeddings, then computes
    the cosine similarity between them. If the similarity is below a given threshold, the output is considered
    not relevant to the prompt.
    """

    def __init__(self, threshold: float = 0):
        """
        Initializes an instance of the Relevance class.

        Parameters:
            threshold (float): The minimum cosine similarity (-1 to 1) between the prompt and output for the output to
                              be considered relevant.
        """

        self._threshold = threshold

        transformers = lazy_load_dep("transformers")
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(_transformer_name)
        self._model = transformers.AutoModel.from_pretrained(_transformer_name).to(device())

        logger.debug(f"Initialized sentence transformer {_transformer_name} on device {device()}")

    def _get_embedding(self, input_str: str):
        encoded_input = self._tokenizer(
            input_str.lower(), padding=True, truncation=True, return_tensors="pt"
        ).to(device())
        with torch.no_grad():
            model_output = self._model(**encoded_input)
        sentence_embeddings = mean_pooling(
            model_output, encoded_input["attention_mask"], torch_device=device()
        )
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if output.strip() == "":
            return output, True, 0.0

        embedding_prompt = self._get_embedding(prompt)
        embedding_output = self._get_embedding(output)
        similarity = F.cosine_similarity(embedding_prompt, embedding_output).item()

        if similarity < self._threshold:
            logger.warning(
                f"Result is not similar to the prompt. Score {similarity}, threshold {self._threshold}"
            )

            risk_score = round(1 - (similarity + 1) / 2, 2)
            return output, False, risk_score

        logger.debug(
            f"Result is similar to the prompt. Score {similarity}, threshold {self._threshold}"
        )

        return output, True, 0.0
