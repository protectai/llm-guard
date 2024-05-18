from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, cast

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_ner
from llm_guard.util import get_logger, lazy_load_dep

from .base import Scanner

if TYPE_CHECKING:
    import transformers

LOGGER = get_logger()

MODEL_V1 = Model(
    path="guishe/nuner-v1_orgs",
    revision="2e95454e741e5bdcbfabd6eaed5fb03a266cf043",
    onnx_path="protectai/guishe-nuner-v1_orgs-onnx",
    onnx_revision="20c9739f45f6b4d10ba63c62e6fa92f214a12a52",
    onnx_subfolder="",
    pipeline_kwargs={
        "aggregation_strategy": "simple",
    },
)


class BanCompetitors(Scanner):
    """
    Scanner to detect competitors in a prompt.

    It uses a named-entity recognition model to extract organizations from the prompt and compares them to a list of competitors.
    """

    def __init__(
        self,
        competitors: Sequence[str],
        *,
        threshold: float = 0.5,
        redact: bool = True,
        model: Model | None = None,
        use_onnx: bool = False,
    ) -> None:
        """
        Initialize BanCompetitors object.

        Parameters:
            competitors (Sequence[str]): List of competitors to detect.
            threshold (float, optional): Threshold to determine if a competitor is present in the prompt. Default is 0.5.
            redact (bool, optional): Whether to redact the competitor name. Default is True.
            model (Model, optional): Model to use for named-entity recognition. Default is V1 model.
            use_onnx (bool, optional): Whether to use ONNX instead of PyTorch for inference. Default is False.

        Raises:
            ValueError: If no topics are provided.
        """
        if model is None:
            model = MODEL_V1

        self._competitors = competitors
        self._threshold = threshold
        self._redact = redact

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_ner(
            model=model,
            use_onnx=use_onnx,
        )

        transformers = cast("transformers", lazy_load_dep("transformers"))
        self._ner_pipeline = transformers.pipeline(
            "ner", model=tf_model, tokenizer=tf_tokenizer, **model.pipeline_kwargs
        )

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        is_detected = False
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        entities = self._ner_pipeline(prompt)
        assert isinstance(entities, list)
        entities = sorted(entities, key=lambda x: x["end"], reverse=True)

        for entity in entities:
            entity["word"] = entity["word"].strip()
            if entity["word"] not in self._competitors:
                LOGGER.debug("Entity is not a specified competitor", entity=entity["word"])
                continue

            if entity["score"] < self._threshold:
                LOGGER.debug(
                    "Competitor detected but the score is below threshold",
                    entity=entity["word"],
                    score=entity["score"],
                )
                continue

            is_detected = True

            if self._redact:
                text_replace_builder.replace_text_get_insertion_index(
                    "[REDACTED]",
                    entity["start"],
                    entity["end"],
                )

            LOGGER.warning(
                "Competitor detected with score", entity=entity["word"], score=entity["score"]
            )

        if is_detected:
            return text_replace_builder.output_text, False, 1.0

        LOGGER.debug("None of the competitors were detected")

        return prompt, True, 0.0
