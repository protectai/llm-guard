from __future__ import annotations

import copy
from typing import Any, Sequence

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder

from llm_guard.model import Model
from llm_guard.transformers_helpers import get_tokenizer_and_model_for_ner
from llm_guard.util import get_logger, lazy_load_dep, split_text_to_word_chunks

from .base import Scanner

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
        chunk_size: int = 512,
        chunk_overlap_size: int = 40,
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
        self.chunk_length = chunk_size
        self.text_overlap_length = chunk_overlap_size

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_ner(
            model=model,
            use_onnx=use_onnx,
        )

        transformers = lazy_load_dep("transformers")
        self._ner_pipeline = transformers.pipeline(
            "ner", model=tf_model, tokenizer=tf_tokenizer, **model.pipeline_kwargs
        )

    def scan(self, prompt: str) -> tuple[str, bool, float]:
        is_detected = False
        text_replace_builder = TextReplaceBuilder(original_text=prompt)
        entities = self._get_ner_results_for_text(prompt)
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
                "Competitor detected with score",
                entity=entity["word"],
                score=entity["score"],
            )

        if is_detected:
            return text_replace_builder.output_text, False, 1.0

        LOGGER.debug("None of the competitors were detected")

        return prompt, True, -1.0

    def _get_ner_results_for_text(self, text: str) -> list[dict]:
        """The function runs model inference on the provided text.
        The text is split into chunks with n overlapping characters.
        The results are then aggregated and duplications are removed.

        :param text: The text to run inference on
        :type text: str
        :return: List of entity predictions on the word level
        :rtype: List[dict]
        """
        assert self._ner_pipeline is not None
        assert self._ner_pipeline.tokenizer is not None

        model_max_length = self._ner_pipeline.tokenizer.model_max_length
        # calculate inputs based on the text
        # normalize characters to token numbers approximately
        # 1 word ~ 2 tokens ~ 4 characters
        text_tokens_length = len(text.split()) * 2
        chunk_length = self.chunk_length // 2 * 4
        text_overlap_length = self.text_overlap_length // 2 * 4
        text_length = len(text)

        # split text into chunks
        if text_tokens_length <= model_max_length:
            predictions = self._ner_pipeline(text)  # type: ignore
        else:
            LOGGER.info(
                "splitting the text into chunks",
                length=text_tokens_length,
                model_max_length=model_max_length,
            )
            predictions: list[dict[str, Any]] = []
            chunk_indexes = split_text_to_word_chunks(
                text_length, chunk_length, text_overlap_length
            )

            # iterate over text chunks and run inference
            for chunk in chunk_indexes:
                chunk_text = text[chunk.start : chunk.end]
                chunk_preds = self._ner_pipeline(chunk_text)

                assert isinstance(chunk_preds, list)

                # align indexes to match the original text - add to each position the value of chunk_start
                aligned_predictions: list[dict[str, Any]] = []
                for prediction in chunk_preds:
                    prediction_tmp: dict[str, Any] = copy.deepcopy(prediction)
                    prediction_tmp["start"] += chunk.start
                    prediction_tmp["end"] += chunk.start
                    aligned_predictions.append(prediction_tmp)

                predictions.extend(aligned_predictions)

        # remove duplicates
        predictions = [dict(t) for t in {tuple(d.items()) for d in predictions}]
        return predictions
