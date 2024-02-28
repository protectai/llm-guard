from typing import Dict, Optional, Sequence

from llm_guard.input_scanners.code import Code as InputCode
from llm_guard.input_scanners.code import default_model_path

from .base import Scanner


class Code(Scanner):
    """
    A class for scanning if the model output includes code in specific programming languages.

    This class uses the transformers library to detect code snippets in the output of the language model.
    It can be configured to allow or deny specific programming languages.
    """

    def __init__(
        self,
        languages: Sequence[str],
        *,
        model_path: str = default_model_path,
        is_blocked: bool = True,
        threshold: float = 0.5,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the Code class.

        Parameters:
            model_path (str): The path to the model to use for language detection.
            languages (Sequence[str]): The list of programming languages to allow or deny.
            is_blocked (bool): Whether the languages are blocked or allowed. Default is True.
            threshold (float): The threshold for the model output to be considered valid. Default is 0.5.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            model_kwargs (dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (dict, optional): Keyword arguments passed to the pipeline.

        Raises:
            ValueError: If both 'allowed' and 'denied' lists are provided or if both are empty.
        """

        self._scanner = InputCode(
            languages,
            model_path=model_path,
            is_blocked=is_blocked,
            threshold=threshold,
            use_onnx=use_onnx,
            model_kwargs=model_kwargs,
            pipeline_kwargs=pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        return self._scanner.scan(output)
