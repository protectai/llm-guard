"""
Feedback collector for llm-guard scanner results.

This module provides the FeedbackCollector class for collecting structured
feedback on scanner results. It is designed to be fully optional and privacy-first.
"""

from __future__ import annotations

import hashlib
import random
import uuid
from datetime import datetime

from .model import FeedbackCollectorConfig, FeedbackRecord
from .storage import FileStorage, InMemoryStorage, StorageBackend


class FeedbackCollector:
    """
    Collector for feedback on scanner results.
    
    This class provides methods to record scan results and collect user feedback
    on false positives and false negatives. It is designed to be:
    - Fully opt-in (disabled by default)
    - Privacy-first (no raw text by default)
    - Non-invasive (no impact on scanning)
    
    When disabled (config.enabled=False), all methods are no-ops with minimal overhead.
    
    Args:
        config: Configuration for feedback collection behavior.
                If not provided, uses default (disabled) configuration.
    
    Example:
        >>> config = FeedbackCollectorConfig(enabled=True, privacy_level=0)
        >>> collector = FeedbackCollector(config)
        >>> record_id = collector.record_scan(
        ...     scan_type="prompt",
        ...     scanner_results={"Toxicity": {"valid": True, "score": 0.1}},
        ...     prompt="Hello world"
        ... )
        >>> collector.report_feedback(record_id, "false_positive", ["Toxicity"])
    """
    
    def __init__(self, config: FeedbackCollectorConfig | None = None):
        self._config = config or FeedbackCollectorConfig()
        
        # Initialize storage backend based on configuration
        if self._config.enabled:
            self._storage = self._create_storage()
        else:
            # When disabled, don't even create storage
            self._storage = None
    
    def _create_storage(self) -> StorageBackend:
        """Create storage backend based on configuration."""
        if self._config.storage_backend == "file":
            if self._config.storage_path is None:
                raise ValueError("storage_path required for file backend")
            return FileStorage(self._config.storage_path)
        elif self._config.storage_backend == "memory":
            return InMemoryStorage(self._config.max_records)
        else:
            # Custom backend not supported in Phase 2
            raise ValueError(f"Unsupported storage backend: {self._config.storage_backend}")
    
    def record_scan(
        self,
        scan_type: str,
        scanner_results: dict[str, dict[str, bool | float]],
        prompt: str | None = None,
        output: str | None = None,
        metadata: dict | None = None,
    ) -> str | None:
        """
        Record a scan result for potential feedback.
        
        This method creates a FeedbackRecord and stores it according to the
        configured privacy level and storage backend.
        
        Args:
            scan_type: Type of scan ("prompt" or "output").
            scanner_results: Dictionary of scanner results.
                           Expected format: {scanner_name: {"valid": bool, "score": float}}
            prompt: The input prompt (optional, used for hashing/sampling based on privacy_level).
            output: The output text (optional, for output scans).
            metadata: Additional metadata (optional, currently unused).
        
        Returns:
            Record ID if recorded successfully, None if skipped (disabled or sampling).
        """
        # Fast path: if disabled, return immediately
        if not self._config.enabled:
            return None
        
        # Check if we should record based on include_correct setting
        # Only skip if ALL scanners passed AND include_correct is False
        any_failed = any(
            not result.get("valid", True) 
            for result in scanner_results.values()
        )
        if not any_failed and not self._config.include_correct:
            return None
        
        # Apply sampling rate
        if self._config.sampling_rate < 1.0:
            if random.random() > self._config.sampling_rate:
                return None
        
        # Generate record ID
        record_id = str(uuid.uuid4())
        
        # Create record with privacy-appropriate data
        record = FeedbackRecord(
            record_id=record_id,
            timestamp=datetime.now(),
            scan_type=scan_type,
            scanner_results=scanner_results,
            prompt_hash=self._hash_text(prompt) if prompt else None,
            output_hash=self._hash_text(output) if output else None,
            prompt_length=len(prompt) if prompt else 0,
            output_length=len(output) if output else None,
            llm_guard_version=self._get_llm_guard_version(),
            prompt_sample=self._get_text_sample(prompt) if prompt else None,
            output_sample=self._get_text_sample(output) if output else None,
        )
        
        # Store the record
        if self._storage:
            self._storage.add(record)
        
        return record_id
    
    def report_feedback(
        self,
        record_id: str,
        feedback_type: str,
        reported_scanners: list[str],
        comment: str | None = None,
    ) -> bool:
        """
        Add user feedback to an existing record.
        
        This method updates a previously recorded scan with user feedback
        about false positives or false negatives.
        
        Args:
            record_id: ID of the record to update.
            feedback_type: Type of feedback ("false_positive", "false_negative", or "correct").
            reported_scanners: List of scanner names being reported.
            comment: Optional free-text comment from user.
        
        Returns:
            True if feedback was added successfully, False otherwise.
        """
        # Fast path: if disabled, return immediately
        if not self._config.enabled or not self._storage:
            return False
        
        # Find the record
        records = self._storage.list()
        for record in records:
            if record.record_id == record_id:
                # Update the record
                record.feedback_type = feedback_type
                record.reported_scanners = reported_scanners
                record.user_comment = comment
                return True
        
        return False
    
    def get_records(self, filter_by: dict | None = None) -> list[FeedbackRecord]:
        """
        Retrieve feedback records with optional filtering.
        
        Args:
            filter_by: Optional dictionary of filters (currently unused in Phase 2).
        
        Returns:
            List of feedback records.
        """
        # Fast path: if disabled, return empty list
        if not self._config.enabled or not self._storage:
            return []
        
        records = self._storage.list()
        
        # Simple filtering (Phase 2: basic implementation)
        if filter_by:
            filtered = []
            for record in records:
                match = True
                
                if "feedback_type" in filter_by:
                    if record.feedback_type != filter_by["feedback_type"]:
                        match = False
                
                if "scan_type" in filter_by:
                    if record.scan_type != filter_by["scan_type"]:
                        match = False
                
                if match:
                    filtered.append(record)
            
            return filtered
        
        return records
    
    def clear_records(self) -> int:
        """
        Clear all records.
        
        Returns:
            Count of cleared records.
        """
        # Fast path: if disabled, return 0
        if not self._config.enabled or not self._storage:
            return 0
        
        return self._storage.clear()
    
    def get_stats(self) -> dict:
        """
        Get summary statistics about collected feedback.
        
        Returns:
            Dictionary with statistics.
        """
        # Fast path: if disabled, return empty stats
        if not self._config.enabled or not self._storage:
            return {
                "total_records": 0,
                "enabled": False,
            }
        
        records = self._storage.list()
        
        # Count feedback types
        feedback_counts = {
            "false_positive": 0,
            "false_negative": 0,
            "correct": 0,
            "no_feedback": 0,
        }
        
        for record in records:
            if record.feedback_type:
                feedback_counts[record.feedback_type] = feedback_counts.get(record.feedback_type, 0) + 1
            else:
                feedback_counts["no_feedback"] += 1
        
        return {
            "total_records": len(records),
            "enabled": self._config.enabled,
            "privacy_level": self._config.privacy_level,
            "storage_backend": self._config.storage_backend,
            "feedback_counts": feedback_counts,
        }
    
    def _hash_text(self, text: str | None) -> str | None:
        """Generate SHA256 hash of text."""
        if text is None:
            return None
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _get_text_sample(self, text: str | None) -> str | None:
        """Get text sample based on privacy level."""
        if text is None:
            return None
        
        # Privacy level 0: no samples
        if self._config.privacy_level == 0:
            return None
        
        # Privacy level 1: first 50 characters
        if self._config.privacy_level == 1:
            return text[:50] if len(text) > 50 else text
        
        # Privacy level 2+: full text (anonymization would be in Phase 3+)
        return text
    
    def _get_llm_guard_version(self) -> str:
        """Get llm-guard version."""
        try:
            import llm_guard
            return getattr(llm_guard, '__version__', 'unknown')
        except ImportError:
            return 'unknown'
