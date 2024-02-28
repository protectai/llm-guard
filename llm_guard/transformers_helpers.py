import importlib
from functools import lru_cache
from typing import Literal, Optional, Union, get_args

from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    TFPreTrainedModel,
)

from .exception import LLMGuardValidationError
from .util import device, get_logger, lazy_load_dep

LOGGER = get_logger()


@lru_cache(maxsize=None)  # Set maxsize=None for an unbounded cache
def get_tokenizer(model_identifier: str, **kwargs):
    """
    This function loads a tokenizer given a model identifier and caches it.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model_identifier (str): The model identifier to load the tokenizer for.
    """
    transformers = lazy_load_dep("transformers")
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_identifier, **kwargs)
    return tokenizer


@lru_cache(maxsize=None)  # Unbounded cache
def is_onnx_supported() -> bool:
    is_supported = importlib.util.find_spec("optimum.onnxruntime") is not None
    if not is_supported:
        LOGGER.warning(
            "ONNX Runtime is not available. "
            "Please install optimum: "
            "`pip install llm-guard[onnxruntime]` for CPU or "
            "`pip install llm-guard[onnxruntime-gpu]` for GPU to enable ONNX Runtime optimizations."
        )

    return is_supported


def _ort_model_for_sequence_classification(
    model: str, export: bool = False, subfolder: str = "", **kwargs
):
    if device().type == "cuda":
        optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime-gpu]")
        tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
            model,
            export=export,
            subfolder=subfolder,
            file_name="model.onnx",
            provider="CUDAExecutionProvider",
            use_io_binding=True,
            **kwargs,
        )

        LOGGER.debug("Initialized classification ONNX model", model=model, device=device())

        return tf_model

    optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
    tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
        model,
        export=export,
        subfolder=subfolder,
        file_name="model.onnx",
        **kwargs,
    )
    LOGGER.debug("Initialized classification ONNX model", model=model, device=device())

    return tf_model


def get_tokenizer_and_model_for_classification(
    model: str, onnx_model: Optional[str] = None, use_onnx: bool = False, **kwargs
):
    """
    This function loads a tokenizer and model given a model identifier and caches them.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model (str): The model identifier to load the tokenizer and model for.
        onnx_model (Optional[str]): The model identifier to load the ONNX model for. Defaults to None.
        use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        **kwargs: Keyword arguments to pass to the tokenizer and model.
    """
    tf_tokenizer = get_tokenizer(model, **kwargs)
    transformers = lazy_load_dep("transformers")

    if kwargs.get("max_length", None) is None:
        kwargs["max_length"] = tf_tokenizer.model_max_length

    if use_onnx and is_onnx_supported() is False:
        LOGGER.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
        use_onnx = False

    if use_onnx is False:
        tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(model, **kwargs)
        LOGGER.debug("Initialized classification model", model=model, device=device())

        return tf_tokenizer, tf_model

    subfolder = "onnx" if onnx_model == model else ""
    if onnx_model is not None:
        model = onnx_model

    # Hack for some models
    tf_tokenizer.model_input_names = ["input_ids", "attention_mask"]

    tf_model = _ort_model_for_sequence_classification(
        model, export=onnx_model is None, subfolder=subfolder, **kwargs
    )

    return tf_tokenizer, tf_model


ClassificationTask = Literal["text-classification", "zero-shot-classification"]


def pipeline(
    task: str,
    model: Union[PreTrainedModel, TFPreTrainedModel],
    tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    **kwargs,
):
    if task not in get_args(ClassificationTask):
        raise LLMGuardValidationError(f"Invalid task. Must be one of {ClassificationTask}")

    transformers = lazy_load_dep("transformers")
    return transformers.pipeline(
        task,
        model=model,
        tokenizer=tokenizer,
        device=device(),
        batch_size=1,
        **kwargs,
    )
