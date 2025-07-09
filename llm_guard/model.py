from __future__ import annotations

import dataclasses

from .util import device


@dataclasses.dataclass
class Model:
    """
    Dataclass to store model information.

    Attributes:
        path (str): Path to the model.
        subfolder (str): Subfolder in the model path.
        revision (str, optional): Revision of the model.
        onnx_path (str, optional): Path to the ONNX model.
        onnx_revision (str, optional): Revision of the ONNX model.
        onnx_subfolder (str): Subfolder in the ONNX model path.
        kwargs (Dict, optional): Keyword arguments passed to the model (transformers).
        pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline (transformers).
    """

    path: str
    subfolder: str = ""
    revision: str | None = None
    onnx_path: str | None = None
    onnx_revision: str | None = None
    onnx_subfolder: str = ""
    onnx_filename: str = "model.onnx"
    kwargs: dict = dataclasses.field(default_factory=dict)
    pipeline_kwargs: dict = dataclasses.field(default_factory=dict)
    tokenizer_kwargs: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        # Determine device safely for ONNX compatibility
        try:
            import onnxruntime

            available_providers = onnxruntime.get_available_providers()

            # If ONNX runtime doesn't have CUDA, force CPU device
            if "CUDAExecutionProvider" not in available_providers:
                # Import torch safely to create CPU device
                try:
                    torch = __import__("torch")
                    model_device = torch.device("cpu")
                except ImportError:
                    # Fallback device for ONNX-only installs
                    model_device = "cpu"
            else:
                model_device = device()
        except ImportError:
            # Fallback when ONNX runtime is not available
            model_device = device()

        default_pipeline_kwargs = {
            "batch_size": 1,
            "device": model_device,
        }
        self.pipeline_kwargs = {**default_pipeline_kwargs, **self.pipeline_kwargs}

    def __str__(self):
        return self.path
