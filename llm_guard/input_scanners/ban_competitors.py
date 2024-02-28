from typing import Dict, Optional, Sequence

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from llm_guard.util import device, get_logger, lazy_load_dep

from .base import Scanner

LOGGER = get_logger()

MODEL_BASE = "tomaarsen/span-marker-bert-base-orgs"
MODEL_SMALL = "tomaarsen/span-marker-bert-small-orgs"


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
        model: Optional[str] = None,
        model_kwargs: Optional[Dict] = None,
    ):
        """
        Initialize BanCompetitors object.

        Parameters:
            competitors (Sequence[str]): List of competitors to detect.
            threshold (float, optional): Threshold to determine if a competitor is present in the prompt. Default is 0.5.
            redact (bool, optional): Whether to redact the competitor name. Default is True.
            model (str, optional): Model to use for named-entity recognition. Default is BASE model.
            model_kwargs (Dict, optional): Keyword arguments passed to the model.

        Raises:
            ValueError: If no topics are provided.
        """
        if model is None:
            model = MODEL_BASE

        self._competitors = competitors
        self._threshold = threshold
        self._redact = redact

        span_marker = lazy_load_dep("span_marker", "span-marker")
        self._ner_pipeline = span_marker.SpanMarkerModel.from_pretrained(
            model, labels=["ORG"], **(model_kwargs or {})
        )

        if device().type == "cuda":
            self._ner_pipeline = self._ner_pipeline.cuda()

    def scan(self, prompt: str) -> (str, bool, float):
        is_detected = False
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        entities = self._ner_pipeline.predict(prompt)
        entities = sorted(entities, key=lambda x: x["char_end_index"], reverse=True)
        for entity in entities:
            if entity["span"] not in self._competitors:
                LOGGER.debug("Entity is not a specified competitor", entity=entity["span"])
                continue

            if entity["score"] < self._threshold:
                LOGGER.debug(
                    "Competitor detected but the score is below threshold",
                    entity=entity["span"],
                    score=entity["score"],
                )
                continue

            is_detected = True

            if self._redact:
                text_replace_builder.replace_text_get_insertion_index(
                    "[REDACTED]",
                    entity["char_start_index"],
                    entity["char_end_index"],
                )

            LOGGER.warning(
                "Competitor detected with score", entity=entity["span"], score=entity["score"]
            )

        if is_detected:
            return text_replace_builder.output_text, False, 1.0

        LOGGER.debug("None of the competitors were detected")

        return prompt, True, 0.0
