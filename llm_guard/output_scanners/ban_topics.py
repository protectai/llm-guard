from typing import Dict, Optional, Sequence

from llm_guard.input_scanners.ban_topics import BanTopics as InputBanTopics

from .base import Scanner


class BanTopics(Scanner):
    """
    A text scanner that checks whether the generated text output includes banned topics.

    The class uses the zero-shot-classification model from Hugging Face to scan the topics present in the text.
    """

    def __init__(
        self,
        topics: Sequence[str],
        *,
        threshold: float = 0.75,
        model: Optional[str] = None,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes BanTopics with a list of topics and a probability threshold.

        Parameters:
            topics (Sequence[str]): The list of topics to be banned from the text.
            threshold (float): The minimum probability required for a topic to be considered present in the text.
                               Default is 0.75.
            model (Dict, optional): The name of the zero-shot-classification model to be used. Default is MODEL_BASE.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.

        Raises:
            ValueError: If no topics are provided.
        """
        self._scanner = InputBanTopics(
            topics,
            threshold=threshold,
            model=model,
            use_onnx=use_onnx,
            model_kwargs=model_kwargs,
            pipeline_kwargs=pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
