from typing import Dict

from pydantic import BaseModel


class AnalyzePromptRequest(BaseModel):
    prompt: str


class AnalyzePromptResponse(BaseModel):
    sanitized_prompt: str
    is_valid: bool
    scanners: Dict[str, float]


class AnalyzeOutputRequest(BaseModel):
    prompt: str
    output: str


class AnalyzeOutputResponse(BaseModel):
    sanitized_output: str
    is_valid: bool
    scanners: Dict[str, float]


class ScanPromptRequest(AnalyzePromptRequest):
    pass


class ScanPromptResponse(BaseModel):
    is_valid: bool
    scanners: Dict[str, float]
