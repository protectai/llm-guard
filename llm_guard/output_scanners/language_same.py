from typing import Dict, Optional

from llm_guard.input_scanners.language import model_path
from llm_guard.transformers_helpers import pipeline
from llm_guard.util import get_logger

from .base import Scanner

LOGGER = get_logger(__name__)


class LanguageSame(Scanner):
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.1,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the LanguageSame scanner.

        Parameters:
            threshold (float): Minimum confidence score
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """

        self._threshold = threshold

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = 512
        transformers_kwargs["truncation"] = True
        transformers_kwargs["top_k"] = None

        self._pipeline = pipeline(
            task="text-classification",
            model=model_path[0],
            onnx_model=model_path[1],
            use_onnx=use_onnx,
            **transformers_kwargs,
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
