"""
Feedback capture module for llm-guard.

This module provides data models and collection logic for structured feedback
on scanner results. It is designed to be fully optional and privacy-first.

Phase 1: Data models (FeedbackRecord, FeedbackCollectorConfig)
Phase 2: Collector and storage backends
Phase 3: Wrapper functions (in .wrapper module)
"""

from .collector import FeedbackCollector
from .model import FeedbackCollectorConfig, FeedbackRecord
from .storage import FileStorage, InMemoryStorage, StorageBackend

# Note: wrapper module is available but not re-exported
# Use: from llm_guard.feedback.wrapper import scan_prompt_with_feedback

__all__ = [
    "FeedbackRecord",
    "FeedbackCollectorConfig",
    "FeedbackCollector",
    "StorageBackend",
    "InMemoryStorage",
    "FileStorage",
]
