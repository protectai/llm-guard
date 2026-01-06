"""
Data models for feedback capture.

This module defines the core data structures for collecting feedback on scanner results.
All models are designed to be privacy-first with configurable privacy levels.

Privacy Levels:
    0 (Default): Metadata only (hashes, lengths, scores) - no raw text
    1: Include text samples (first N characters)
    2: Include anonymized text (PII removed)
    3: Include full raw text (requires explicit user consent)
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import Literal

# Type aliases for clarity
FeedbackType = Literal["false_positive", "false_negative", "correct"]
ScanType = Literal["prompt", "output"]
StorageBackend = Literal["memory", "file", "custom"]


@dataclasses.dataclass
class FeedbackRecord:
    """
    Represents a single feedback event for a scanner result.

    This dataclass stores metadata about a scan and optional user feedback.
    By default (privacy_level=0), no raw prompt or output text is stored.

    Attributes:
        record_id: Unique identifier for this feedback record (UUID recommended).
        timestamp: When this feedback was recorded.
        scan_type: Type of scan ("prompt" or "output").
        scanner_results: Dictionary mapping scanner names to their results.
                        Expected format: {scanner_name: {"valid": bool, "score": float}}
        feedback_type: Type of feedback provided by user.
        reported_scanners: List of scanner names being reported on.
        user_comment: Optional free-text comment from user.
        prompt_hash: SHA256 hash of the prompt (for identification without storage).
        output_hash: SHA256 hash of the output (for output scans only).
        prompt_length: Character count of the prompt.
        output_length: Character count of the output (for output scans only).
        scanner_versions: Dictionary mapping scanner names to version/config identifiers.
        llm_guard_version: Version of llm-guard package at time of recording.
        prompt_sample: Optional text sample or anonymized prompt (privacy level 1+).
        output_sample: Optional text sample or anonymized output (privacy level 1+).
    """

    # Identifiers
    record_id: str
    timestamp: datetime

    # Scan context
    scan_type: ScanType
    scanner_results: dict[str, dict[str, bool | float]]

    # Feedback (optional, can be added after initial recording)
    feedback_type: FeedbackType | None = None
    reported_scanners: list[str] = dataclasses.field(default_factory=list)
    user_comment: str | None = None

    # Privacy-safe metadata (always collected)
    prompt_hash: str | None = None
    output_hash: str | None = None
    prompt_length: int = 0
    output_length: int | None = None

    # Scanner metadata
    scanner_versions: dict[str, str] = dataclasses.field(default_factory=dict)
    llm_guard_version: str = ""

    # Optional text data (requires privacy_level > 0)
    prompt_sample: str | None = None
    output_sample: str | None = None


@dataclasses.dataclass
class FeedbackCollectorConfig:
    """
    Configuration for feedback collection behavior.

    This dataclass defines how feedback should be collected, stored, and what
    data should be included based on privacy preferences.

    Attributes:
        enabled: Master switch for feedback collection. When False, all collection
                is disabled (no-op behavior).
        privacy_level: Controls what data is collected (0-3).
                      0 = metadata only (default, most private)
                      1 = include text samples (first N chars)
                      2 = include anonymized text (PII removed)
                      3 = include full raw text (requires explicit consent)
        storage_backend: Where to store feedback records.
        storage_path: File path for file-based storage (required if backend="file").
        max_records: Maximum number of records to keep in memory. When exceeded,
                    oldest records are dropped (FIFO) unless auto_flush is enabled.
        sampling_rate: Fraction of scans to record (0.0-1.0). Use <1.0 for
                      high-volume scenarios to reduce overhead.
        include_correct: Whether to record feedback for scans that passed all
                        scanners. Default False (only record failures).
        auto_flush: Whether to automatically flush records to storage when
                   max_records is reached. Requires storage_backend="file".
    """

    # Core settings
    enabled: bool = False
    privacy_level: int = 0

    # Storage settings
    storage_backend: StorageBackend = "memory"
    storage_path: str | None = None

    # Performance and capacity settings
    max_records: int = 1000
    sampling_rate: float = 1.0

    # Collection behavior
    include_correct: bool = False
    auto_flush: bool = False

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not 0 <= self.privacy_level <= 3:
            raise ValueError(f"privacy_level must be 0-3, got {self.privacy_level}")

        if not 0.0 <= self.sampling_rate <= 1.0:
            raise ValueError(f"sampling_rate must be 0.0-1.0, got {self.sampling_rate}")

        if self.max_records < 1:
            raise ValueError(f"max_records must be >= 1, got {self.max_records}")

        if self.storage_backend == "file" and self.storage_path is None:
            raise ValueError("storage_path is required when storage_backend='file'")

        if self.auto_flush and self.storage_backend != "file":
            raise ValueError("auto_flush requires storage_backend='file'")
