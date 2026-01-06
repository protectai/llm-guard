"""
Storage backends for feedback records.

This module provides a minimal pluggable storage interface with two implementations:
- InMemoryStorage: Bounded in-memory list (default)
- FileStorage: JSON file-based storage (local only)

All storage backends implement a simple interface:
- add(record) -> None
- list() -> list[FeedbackRecord]
- clear() -> int
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import FeedbackRecord


class StorageBackend(ABC):
    """
    Abstract base class for feedback storage backends.
    
    All storage implementations must provide three methods:
    - add: Store a feedback record
    - list: Retrieve all stored records
    - clear: Remove all records and return count
    """
    
    @abstractmethod
    def add(self, record: FeedbackRecord) -> None:
        """Add a feedback record to storage."""
        pass
    
    @abstractmethod
    def list(self) -> list[FeedbackRecord]:
        """Retrieve all stored feedback records."""
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """Clear all records and return the count of cleared records."""
        pass


class InMemoryStorage(StorageBackend):
    """
    In-memory storage backend with bounded capacity.
    
    Records are stored in a list with a maximum capacity. When the limit
    is exceeded, the oldest records are dropped (FIFO).
    
    This is the default storage backend.
    
    Args:
        max_records: Maximum number of records to keep in memory.
    """
    
    def __init__(self, max_records: int = 1000):
        if max_records < 1:
            raise ValueError(f"max_records must be >= 1, got {max_records}")
        
        self._max_records = max_records
        self._records: list[FeedbackRecord] = []
    
    def add(self, record: FeedbackRecord) -> None:
        """Add a record, dropping oldest if at capacity."""
        self._records.append(record)
        
        # Drop oldest records if over capacity
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]
    
    def list(self) -> list[FeedbackRecord]:
        """Return a copy of all records."""
        return self._records.copy()
    
    def clear(self) -> int:
        """Clear all records and return count."""
        count = len(self._records)
        self._records.clear()
        return count


class FileStorage(StorageBackend):
    """
    File-based storage backend using JSON serialization.
    
    Records are stored in a JSON file on the local filesystem.
    The file is overwritten on each save operation (simple, safe).
    
    File permissions are set to 0600 (owner read/write only) for security.
    
    Args:
        file_path: Path to the JSON file for storage.
    """
    
    def __init__(self, file_path: str):
        if not file_path:
            raise ValueError("file_path cannot be empty")
        
        self._file_path = Path(file_path)
        self._records: list[FeedbackRecord] = []
        
        # Load existing records if file exists
        if self._file_path.exists():
            self._load()
    
    def add(self, record: FeedbackRecord) -> None:
        """Add a record and save to file."""
        self._records.append(record)
        self._save()
    
    def list(self) -> list[FeedbackRecord]:
        """Return a copy of all records."""
        return self._records.copy()
    
    def clear(self) -> int:
        """Clear all records, delete file, and return count."""
        count = len(self._records)
        self._records.clear()
        
        # Delete the file if it exists
        if self._file_path.exists():
            self._file_path.unlink()
        
        return count
    
    def _load(self) -> None:
        """Load records from JSON file."""
        from .model import FeedbackRecord
        
        try:
            with open(self._file_path, 'r') as f:
                data = json.load(f)
            
            # Deserialize records
            self._records = []
            for item in data:
                # Convert timestamp string back to datetime
                if 'timestamp' in item and isinstance(item['timestamp'], str):
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                
                self._records.append(FeedbackRecord(**item))
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # If file is corrupted, start fresh
            self._records = []
    
    def _save(self) -> None:
        """Save records to JSON file."""
        # Ensure parent directory exists
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize records
        data = []
        for record in self._records:
            record_dict = {
                'record_id': record.record_id,
                'timestamp': record.timestamp.isoformat(),
                'scan_type': record.scan_type,
                'scanner_results': record.scanner_results,
                'feedback_type': record.feedback_type,
                'reported_scanners': record.reported_scanners,
                'user_comment': record.user_comment,
                'prompt_hash': record.prompt_hash,
                'output_hash': record.output_hash,
                'prompt_length': record.prompt_length,
                'output_length': record.output_length,
                'scanner_versions': record.scanner_versions,
                'llm_guard_version': record.llm_guard_version,
                'prompt_sample': record.prompt_sample,
                'output_sample': record.output_sample,
            }
            data.append(record_dict)
        
        # Write to file with secure permissions
        with open(self._file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Set file permissions to 0600 (owner read/write only)
        os.chmod(self._file_path, 0o600)
