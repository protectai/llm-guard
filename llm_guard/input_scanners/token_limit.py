import logging
from typing import List, Optional

import tiktoken

from .base import Scanner

log = logging.getLogger(__name__)


class TokenLimit(Scanner):
    """
    A token limit scanner based on the tiktoken library. It checks if a prompt exceeds a specific token limit
    and can split a large prompt into chunks of text that each fit within the limit.
    """

    def __init__(
        self,
        limit: int = 4096,
        encoding_name: str = "cl100k_base",
        model_name: Optional[str] = None,
    ):
        """
        Initializes TokenLimit with a limit, encoding name, and model name.

        Parameters:
            limit (int): Maximum number of tokens allowed in a prompt. Default is 4096.
            encoding_name (str): Encoding model for the tiktoken library. Default is 'cl100k_base'.
            model_name (str): Specific model for the tiktoken encoding. Default is None.

        Raises:
            None.
        """

        self._limit = limit

        if not model_name:
            self._encoding = tiktoken.get_encoding(encoding_name)
        else:
            self._encoding = tiktoken.encoding_for_model(model_name)

    def _split_text_on_tokens(self, text: str) -> (List[str], int):
        """Split incoming text and return chunks using tokenizer."""
        splits: List[str] = []
        input_ids = self._encoding.encode(text)
        start_idx = 0
        cur_idx = min(start_idx + self._limit, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]
        while start_idx < len(input_ids):
            splits.append(self._encoding.decode(chunk_ids))
            start_idx += self._limit
            cur_idx = min(start_idx + self._limit, len(input_ids))
            chunk_ids = input_ids[start_idx:cur_idx]
        return splits, len(input_ids)

    def scan(self, prompt: str) -> (str, bool, float):
        if prompt.strip() == "":
            return prompt, True, 0.0

        chunks, num_tokens = self._split_text_on_tokens(text=prompt)
        if num_tokens < self._limit:
            log.debug(f"Prompt fits the maximum tokens: {num_tokens}, max: {self._limit}")
            return prompt, True, 0.0

        log.warning(f"Prompt is too big ({num_tokens} tokens). Split into chunks: {chunks}")

        return chunks[0], False, 1.0
