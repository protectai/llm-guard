from typing import Dict

from pydantic import BaseModel


class ScanPromptRequest(BaseModel):
    prompt: str


class ScanPromptResponse(BaseModel):
    is_valid: bool
    scanners: Dict[str, float]


class AnalyzePromptRequest(ScanPromptRequest):
    pass


class AnalyzePromptResponse(ScanPromptResponse):
    sanitized_prompt: str


class ScanOutputRequest(BaseModel):
    prompt: str
    output: str


class ScanOutputResponse(BaseModel):
    is_valid: bool
    scanners: Dict[str, float]


class AnalyzeOutputRequest(ScanOutputRequest):
    pass


class AnalyzeOutputResponse(ScanOutputResponse):
    sanitized_output: str
