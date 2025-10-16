from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ScanPromptRequest(BaseModel):
    prompt: str = Field(title="Prompt")
    scanners_suppress: List[str] = Field(title="Scanners to suppress", default=[])


class ScanPromptResponse(BaseModel):
    is_valid: bool = Field(title="Whether the prompt is safe")
    scanners: Dict[str, float] = Field(title="Risk scores of individual scanners")


class AnalyzePromptRequest(ScanPromptRequest):
    pass


class AnalyzePromptResponse(ScanPromptResponse):
    sanitized_prompt: str = Field(title="Sanitized prompt")


class ScanOutputRequest(BaseModel):
    prompt: str = Field(title="Prompt")
    output: str = Field(title="Model output")
    scanners_suppress: List[str] = Field(title="Scanners to suppress", default=[])


class ScanOutputResponse(BaseModel):
    is_valid: bool = Field(title="Whether the output is safe")
    scanners: Dict[str, float] = Field(title="Risk scores of individual scanners")


class AnalyzeOutputRequest(ScanOutputRequest):
    pass


class AnalyzeOutputResponse(ScanOutputResponse):
    sanitized_output: str = Field(title="Sanitized output")


# Batch processing schemas for prompts
class BatchScanPromptRequest(BaseModel):
    prompts: List[str] = Field(title="List of prompts to process")
    scanners_suppress: List[str] = Field(title="Shared scanners to suppress", default=[])


class BatchAnalyzePromptRequest(BatchScanPromptRequest):
    pass


class BatchPromptResult(BaseModel):
    prompt_index: int = Field(title="Index of the prompt in the batch")
    is_valid: bool = Field(title="Whether the prompt is safe")
    scanners: Dict[str, float] = Field(title="Risk scores of individual scanners")
    error: Optional[str] = Field(title="Error message if processing failed", default=None)


class BatchScanPromptResponse(BaseModel):
    results: List[BatchPromptResult] = Field(title="Results for each prompt")
    total_processed: int = Field(title="Total number of prompts processed")
    total_valid: int = Field(title="Number of valid prompts")
    processing_time: float = Field(title="Total processing time in seconds")


class BatchAnalyzePromptResult(BatchPromptResult):
    sanitized_prompt: str = Field(title="Sanitized prompt text")


class BatchAnalyzePromptResponse(BaseModel):
    results: List[BatchAnalyzePromptResult] = Field(title="Results for each prompt")
    total_processed: int = Field(title="Total number of prompts processed")
    total_valid: int = Field(title="Number of valid prompts")
    processing_time: float = Field(title="Total processing time in seconds")
