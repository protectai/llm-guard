import dataclasses
from typing import Dict, Optional


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
    revision: Optional[str] = None
    onnx_path: Optional[str] = None
    onnx_revision: Optional[str] = None
    onnx_subfolder: str = ""
    onnx_filename: str = "model.onnx"
    onnx_enable_hack: bool = True  # Enable hack to remove token_type_ids from input
    kwargs: Dict = dataclasses.field(default_factory=dict)
    pipeline_kwargs: Dict = dataclasses.field(default_factory=dict)

    def __str__(self):
        return self.path
