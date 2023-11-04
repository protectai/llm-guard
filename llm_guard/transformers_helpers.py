import importlib
from functools import lru_cache

from .util import device, lazy_load_dep, logger


@lru_cache(maxsize=None)  # Unbounded cache
def is_onnx_supported() -> bool:
    is_supported = (
        str(device()) == "cpu" and importlib.util.find_spec("optimum.onnxruntime") is not None
    )
    if not is_supported:
        logger.warning(
            "ONNX Runtime is not available. "
            "Please install optimum: `pip install onnx onnxruntime optimum[onnx-runtime]` to enable ONNX Runtime optimizations."
        )

    return is_supported


def pipeline_text_classification(model: str, use_onnx: bool = False, **kwargs):
    transformers = lazy_load_dep("transformers")
    tf_tokenizer = transformers.AutoTokenizer.from_pretrained(model)

    if use_onnx and is_onnx_supported() is False:
        logger.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
        use_onnx = False

    if use_onnx:
        optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
        tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
            model, export=True
        )
        logger.debug(
            f"Initialized text-classification pipeline for ONNX model {model} on device {device()}"
        )
    else:
        tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(model)
        logger.debug(
            f"Initialized text-classification pipeline for model {model} on device {device()}"
        )

    if kwargs.get("max_length", None) is None:
        kwargs["max_length"] = tf_tokenizer.model_max_length

    return transformers.pipeline(
        "text-classification",
        model=tf_model,
        tokenizer=tf_tokenizer,
        device=device(),
        **kwargs,
    )


def pipeline_ner(model: str, use_onnx: bool = False, **kwargs):
    transformers = lazy_load_dep("transformers")
    tf_tokenizer = transformers.AutoTokenizer.from_pretrained(model)

    if use_onnx and is_onnx_supported() is False:
        logger.warning("ONNX is not supported on this machine. Using PyTorch instead of ONNX.")
        use_onnx = False

    if use_onnx:
        optimum_onnxruntime = lazy_load_dep("optimum.onnxruntime", "optimum[onnxruntime]")
        tf_model = optimum_onnxruntime.ORTModelForTokenClassification.from_pretrained(
            model, export=True
        )
        logger.debug(f"Initialized ner pipeline for ONNX model {model} on device {device()}")
    else:
        tf_model = transformers.AutoModelForTokenClassification.from_pretrained(model)
        logger.debug(f"Initialized ner pipeline for model {model} on device {device()}")

    return transformers.pipeline(
        "ner",
        model=tf_model,
        tokenizer=tf_tokenizer,
        device=device(),
        **kwargs,
    )
