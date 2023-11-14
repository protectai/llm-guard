from llm_guard.input_scanners.language import model_path
from llm_guard.transformers_helpers import pipeline_text_classification
from llm_guard.util import logger

from .base import Scanner


class LanguageSame(Scanner):
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(
        self,
        threshold: float = 0.1,
        use_onnx: bool = False,
    ):
        """
        Initializes the LanguageSame scanner.

        Parameters:
            threshold (float): Minimum confidence score
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
        """

        self._threshold = threshold
        self._pipeline = pipeline_text_classification(
            model=model_path[0],
            onnx_model=model_path[1],
            top_k=None,
            use_onnx=use_onnx,
            truncation=True,
            max_length=512,
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
            logger.warning(f"None of languages are above found in the prompt")
            return output, False, 1.0

        if len(output_languages) == 0:
            logger.warning(f"None of languages are above threshold found in the output")
            return output, False, 1.0

        common_languages = list(set(prompt_languages).intersection(output_languages))
        if len(common_languages) == 0:
            logger.warning(f"No common languages in the output and prompt: {common_languages}")
            return output, False, 1.0

        logger.debug(f"Languages {common_languages} are found in the prompt and output")
        return output, True, 0.0
