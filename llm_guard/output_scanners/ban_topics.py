from __future__ import annotations

from llm_guard.input_scanners.ban_topics import BanTopics as InputBanTopics
from llm_guard.model import Model

from .base import Scanner


class BanTopics(Scanner):
    """
    A text scanner that checks whether the generated text output includes banned topics.

    The class uses the zero-shot-classification model from Hugging Face to scan the topics present in the text.
    """

    def __init__(
        self,
        topics: list[str],
        *,
        threshold: float = 0.75,
        model: Model | None = None,
        use_onnx: bool = False,
    ) -> None:
        """
        Initializes BanTopics with a list of topics and a probability threshold.

        Parameters:
            topics: The list of topics to be banned from the text.
            threshold: The minimum probability required for a topic to be considered present in the text.
                               Default is 0.75.
            model: The name of the zero-shot-classification model to be used. Default is MODEL_BASE.
            use_onnx: Whether to use ONNX for inference. Default is False.

        Raises:
            ValueError: If no topics are provided.
        """
        self._scanner = InputBanTopics(
            topics,
            threshold=threshold,
            model=model,
            use_onnx=use_onnx,
        )

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
