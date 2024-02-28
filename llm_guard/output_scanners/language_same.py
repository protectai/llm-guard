from typing import Dict, Optional

from llm_guard.input_scanners.language import default_model_path
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_classification, pipeline
from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger()


class LanguageSame(Scanner):
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(
        self,
        *,
        model_path: Optional[str] = None,
        threshold: float = 0.1,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the LanguageSame scanner.

        Parameters:
            model_path (str): The path to the model. Default is None.
            threshold (float): Minimum confidence score
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.
            pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline.
        """

        self._threshold = threshold

        default_pipeline_kwargs = {
            "max_length": 512,
            "truncation": True,
            "top_k": None,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        onnx_model_path = model_path
        if model_path is None:
            model_path = default_model_path[0]
            onnx_model_path = default_model_path[1]

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path, onnx_model=onnx_model_path, use_onnx=use_onnx, **model_kwargs
        )

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
        )

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        if prompt.strip() == "" or output.strip() == "":
            return prompt, True, 0.0

        detected_languages = self._pipeline([prompt, output])
        prompt_languages = [
            detected_language["label"]
            for detected_language in detected_languages[0]
            if detected_language["score"] > self._threshold
        ]
        output_languages = [
            detected_language["label"]
            for detected_language in detected_languages[1]
            if detected_language["score"] > self._threshold
        ]

        if len(prompt_languages) == 0:
            LOGGER.warning("None of languages are above found in the prompt")
            return output, False, 1.0

        if len(output_languages) == 0:
            LOGGER.warning("None of languages are above threshold found in the output")
            return output, False, 1.0

        common_languages = list(set(prompt_languages).intersection(output_languages))
        if len(common_languages) == 0:
            LOGGER.warning(
                "No common languages in the output and prompt", common_languages=common_languages
            )
            return output, False, 1.0

        LOGGER.debug(
            "Languages are found in the prompt and output", common_languages=common_languages
        )
        return output, True, 0.0
