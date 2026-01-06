"""
Tests for feedback storage backends.

These tests verify the storage abstraction and both implementations
(InMemoryStorage and FileStorage).
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from llm_guard.feedback.model import FeedbackRecord
from llm_guard.feedback.storage import FileStorage, InMemoryStorage, StorageBackend


class TestInMemoryStorage:
    """Tests for InMemoryStorage backend."""
    
    def test_initialization(self):
        """Test creating an InMemoryStorage instance."""
        storage = InMemoryStorage(max_records=100)
        assert storage.list() == []
    
    def test_initialization_validation(self):
        """Test that max_records is validated."""
        with pytest.raises(ValueError, match="max_records must be >= 1"):
            InMemoryStorage(max_records=0)
        
        with pytest.raises(ValueError, match="max_records must be >= 1"):
            InMemoryStorage(max_records=-1)
    
    def test_add_and_list(self):
        """Test adding records and listing them."""
        storage = InMemoryStorage()
        
        record1 = FeedbackRecord(
            record_id="test-1",
            timestamp=datetime.now(),
            scan_type="prompt",
            scanner_results={"Toxicity": {"valid": True, "score": 0.1}},
        )
        
        record2 = FeedbackRecord(
            record_id="test-2",
            timestamp=datetime.now(),
            scan_type="output",
            scanner_results={"Bias": {"valid": False, "score": 0.9}},
        )
        
        storage.add(record1)
        storage.add(record2)
        
        records = storage.list()
        assert len(records) == 2
        assert records[0].record_id == "test-1"
        assert records[1].record_id == "test-2"
    
    def test_max_records_limit(self):
        """Test that storage respects max_records limit."""
        storage = InMemoryStorage(max_records=3)
        
        # Add 5 records
        for i in range(5):
            record = FeedbackRecord(
                record_id=f"test-{i}",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
        
        # Should only keep last 3
        records = storage.list()
        assert len(records) == 3
        assert records[0].record_id == "test-2"
        assert records[1].record_id == "test-3"
        assert records[2].record_id == "test-4"
    
    def test_clear(self):
        """Test clearing all records."""
        storage = InMemoryStorage()
        
        # Add some records
        for i in range(5):
            record = FeedbackRecord(
                record_id=f"test-{i}",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
        
        # Clear and verify count
        count = storage.clear()
        assert count == 5
        assert storage.list() == []
    
    def test_list_returns_copy(self):
        """Test that list() returns a copy, not the internal list."""
        storage = InMemoryStorage()
        
        record = FeedbackRecord(
            record_id="test-1",
            timestamp=datetime.now(),
            scan_type="prompt",
            scanner_results={},
        )
        storage.add(record)
        
        # Get list and modify it
        records = storage.list()
        records.clear()
        
        # Original should be unchanged
        assert len(storage.list()) == 1


class TestFileStorage:
    """Tests for FileStorage backend."""
    
    def test_initialization_new_file(self):
        """Test creating FileStorage with a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            storage = FileStorage(str(file_path))
            
            assert storage.list() == []
            assert not file_path.exists()  # File not created until first add
    
    def test_initialization_validation(self):
        """Test that file_path is validated."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            FileStorage("")
    
    def test_add_and_save(self):
        """Test adding records and saving to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            storage = FileStorage(str(file_path))
            
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={"Toxicity": {"valid": True, "score": 0.1}},
            )
            
            storage.add(record)
            
            # File should exist
            assert file_path.exists()
            
            # Verify records
            records = storage.list()
            assert len(records) == 1
            assert records[0].record_id == "test-1"
    
    def test_load_existing_file(self):
        """Test loading records from an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            
            # Create and populate storage
            storage1 = FileStorage(str(file_path))
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={"Toxicity": {"valid": True, "score": 0.1}},
            )
            storage1.add(record)
            
            # Create new storage instance (should load from file)
            storage2 = FileStorage(str(file_path))
            records = storage2.list()
            
            assert len(records) == 1
            assert records[0].record_id == "test-1"
    
    def test_clear_deletes_file(self):
        """Test that clear() deletes the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            storage = FileStorage(str(file_path))
            
            # Add a record
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
            assert file_path.exists()
            
            # Clear
            count = storage.clear()
            assert count == 1
            assert not file_path.exists()
            assert storage.list() == []
    
    def test_file_permissions(self):
        """Test that file is created with secure permissions (0600)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            storage = FileStorage(str(file_path))
            
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
            
            # Check file permissions
            import stat
            file_stat = file_path.stat()
            file_mode = stat.S_IMODE(file_stat.st_mode)
            
            # Should be 0600 (owner read/write only)
            assert file_mode == 0o600
    
    def test_corrupted_file_handling(self):
        """Test that corrupted JSON files are handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            
            # Write corrupted JSON
            with open(file_path, 'w') as f:
                f.write("{ invalid json }")
            
            # Should not crash, should start fresh
            storage = FileStorage(str(file_path))
            assert storage.list() == []
    
    def test_parent_directory_creation(self):
        """Test that parent directories are created if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "feedback.json"
            storage = FileStorage(str(file_path))
            
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
            
            assert file_path.exists()
            assert file_path.parent.exists()
    
    def test_list_returns_copy(self):
        """Test that list() returns a copy, not the internal list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            storage = FileStorage(str(file_path))
            
            record = FeedbackRecord(
                record_id="test-1",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
            )
            storage.add(record)
            
            # Get list and modify it
            records = storage.list()
            records.clear()
            
            # Original should be unchanged
            assert len(storage.list()) == 1


class TestStorageBackendInterface:
    """Tests for StorageBackend abstract interface."""
    
    def test_interface_methods(self):
        """Test that StorageBackend defines the required interface."""
        assert hasattr(StorageBackend, 'add')
        assert hasattr(StorageBackend, 'list')
        assert hasattr(StorageBackend, 'clear')
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that StorageBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StorageBackend()
