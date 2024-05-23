from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Literal, get_args

from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    TFPreTrainedModel,
)

from .exception import LLMGuardValidationError
from .model import Model
from .util import device, get_logger, lazy_load_dep

LOGGER = get_logger()


def get_tokenizer(model: Model):
    """
    This function loads a tokenizer given a model identifier and caches it.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model (Model): The model to load the tokenizer for.
    """
    transformers = lazy_load_dep("transformers")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model.path, revision=model.revision, **model.tokenizer_kwargs
    )
    return tokenizer


@lru_cache(maxsize=None)  # Unbounded cache
def is_onnx_supported() -> bool:
    is_supported = importlib.util.find_spec("optimum.onnxruntime") is not None  # type: ignore
    if not is_supported:
        LOGGER.warning(
            "ONNX Runtime is not available. "
            "Please install optimum: "
            "`pip install llm-guard[onnxruntime]` for CPU or "
            "`pip install llm-guard[onnxruntime-gpu]` for GPU to enable ONNX Runtime optimizations."
        )

    return is_supported


def _ort_model_for_sequence_classification(
    model: Model,
):
    provider = "CPUExecutionProvider"
    package_name = "optimum[onnxruntime]"
    if device().type == "cuda":
        package_name = "optimum[onnxruntime-gpu]"
        provider = "CUDAExecutionProvider"

    onnxruntime = lazy_load_dep("optimum.onnxruntime", package_name)

    tf_model = onnxruntime.ORTModelForSequenceClassification.from_pretrained(
        model.onnx_path or model.path,
        export=model.onnx_path is None,
        file_name=model.onnx_filename,
        subfolder=model.onnx_subfolder,
        revision=model.onnx_revision,
        provider=provider,
        **model.kwargs,
    )
    LOGGER.debug("Initialized classification ONNX model", model=model, device=device())

    return tf_model


def get_tokenizer_and_model_for_classification(
    model: Model,
    use_onnx: bool = False,
):
    """
    This function loads a tokenizer and model given a model identifier and caches them.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model (str): The model identifier to load the tokenizer and model for.
        use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
    """
    tf_tokenizer = get_tokenizer(model)
    transformers = lazy_load_dep("transformers")

    if use_onnx and is_onnx_supported() is False:
        LOGGER.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
        use_onnx = False

    if use_onnx is False:
        tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(
            model.path, subfolder=model.subfolder, revision=model.revision, **model.kwargs
        )
        LOGGER.debug("Initialized classification model", model=model, device=device())

        return tf_tokenizer, tf_model

    tf_model = _ort_model_for_sequence_classification(model)

    return tf_tokenizer, tf_model


def get_tokenizer_and_model_for_ner(
    model: Model,
    use_onnx: bool = False,
):
    """
    This function loads a tokenizer and model given a model identifier and caches them.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model (str): The model identifier to load the tokenizer and model for.
        use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
    """
    tf_tokenizer = get_tokenizer(model)
    transformers = lazy_load_dep("transformers")

    if use_onnx and is_onnx_supported() is False:
        LOGGER.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
        use_onnx = False

    if use_onnx is False:
        tf_model = transformers.AutoModelForTokenClassification.from_pretrained(
            model.path, subfolder=model.subfolder, revision=model.revision, **model.kwargs
        )
        LOGGER.debug("Initialized NER model", model=model, device=device())

        return tf_tokenizer, tf_model

    optimum_onnxruntime = lazy_load_dep(
        "optimum.onnxruntime",
        "optimum[onnxruntime]" if device().type != "cuda" else "optimum[onnxruntime-gpu]",
    )

    tf_model = optimum_onnxruntime.ORTModelForTokenClassification.from_pretrained(
        model.onnx_path,
        export=False,
        subfolder=model.onnx_subfolder,
        provider=("CUDAExecutionProvider" if device().type == "cuda" else "CPUExecutionProvider"),
        revision=model.onnx_revision,
        file_name=model.onnx_filename,
        **model.kwargs,
    )
    LOGGER.debug("Initialized NER ONNX model", model=model, device=device())

    return tf_tokenizer, tf_model


ClassificationTask = Literal["text-classification", "zero-shot-classification"]


def pipeline(
    task: str,
    model: PreTrainedModel | TFPreTrainedModel,
    tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
    **kwargs,
):
    if task not in get_args(ClassificationTask):
        raise LLMGuardValidationError(f"Invalid task. Must be one of {ClassificationTask}")

    if kwargs.get("max_length", None) is None:
        kwargs["max_length"] = tokenizer.model_max_length

    transformers = lazy_load_dep("transformers")
    return transformers.pipeline(
        task,
        model=model,
        tokenizer=tokenizer,
        **kwargs,
    )
