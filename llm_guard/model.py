import dataclasses
from typing import Dict, Optional


@dataclasses.dataclass
class Model:
    """
    Dataclass to store model information.

    Attributes:
        path (str): Path to the model.
        subfolder (str): Subfolder in the model path.
        onnx_path (str, optional): Path to the ONNX model.
        onnx_subfolder (str): Subfolder in the ONNX model path.
        kwargs (Dict, optional): Keyword arguments passed to the model (transformers).
        pipeline_kwargs (Dict, optional): Keyword arguments passed to the pipeline (transformers).
    """

    path: str
    subfolder: str = ""
    onnx_path: Optional[str] = None
    onnx_subfolder: str = ""
    onnx_filename: str = "model.onnx"
    kwargs: Dict = dataclasses.field(default_factory=dict)
    pipeline_kwargs: Dict = dataclasses.field(default_factory=dict)

    def __str__(self):
        return self.path
