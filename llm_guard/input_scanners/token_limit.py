from __future__ import annotations

from typing import TYPE_CHECKING, cast

from llm_guard.util import get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()

if TYPE_CHECKING:
    import tiktoken


class TokenLimit(Scanner):
    """
    A token limit scanner based on the tiktoken library. It checks if a prompt exceeds a specific token limit
    and can split a large prompt into chunks of text that each fit within the limit.
    """

    def __init__(
        self,
        *,
        limit: int = 4096,
        encoding_name: str = "cl100k_base",
        model_name: str | None = None,
    ) -> None:
        """
        Initializes TokenLimit with a limit, encoding name, and model name.

        Parameters:
            limit (int): Maximum number of tokens allowed in a prompt. Default is 4096.
            encoding_name (str): Encoding model for the tiktoken library. Default is 'cl100k_base'.
            model_name (str): Specific model for the tiktoken encoding. Default is None.
        """

        self._limit = limit

        tiktoken = cast("tiktoken", lazy_load_dep("tiktoken"))
        if not model_name:
            self._encoding = tiktoken.get_encoding(encoding_name)
        else:
            self._encoding = tiktoken.encoding_for_model(model_name)

    def _split_text_on_tokens(self, text: str) -> tuple[list[str], int]:
        """Split incoming text and return chunks using tokenizer."""
        splits: list[str] = []
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

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        if prompt.strip() == "":
            return prompt, True, 0.0

        chunks, num_tokens = self._split_text_on_tokens(text=prompt)
        if num_tokens < self._limit:
            LOGGER.debug(
                "Prompt fits the maximum tokens", num_tokens=num_tokens, threshold=self._limit
            )
            return prompt, True, 0.0

        LOGGER.warning(
            "Prompt is too big. Splitting into chunks", num_tokens=num_tokens, chunks=chunks
        )

        return chunks[0], False, 1.0
