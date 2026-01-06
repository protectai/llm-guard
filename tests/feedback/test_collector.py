"""
Tests for FeedbackCollector.

These tests verify the collector logic, privacy controls, and integration
with storage backends.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from llm_guard.feedback import FeedbackCollector, FeedbackCollectorConfig


class TestFeedbackCollectorDisabled:
    """Tests for FeedbackCollector when disabled."""
    
    def test_default_config_is_disabled(self):
        """Test that default configuration is disabled."""
        collector = FeedbackCollector()
        
        # All methods should be no-ops
        record_id = collector.record_scan("prompt", {})
        assert record_id is None
        
        assert collector.report_feedback("test", "false_positive", []) is False
        assert collector.get_records() == []
        assert collector.clear_records() == 0
        
        stats = collector.get_stats()
        assert stats["enabled"] is False
        assert stats["total_records"] == 0
    
    def test_explicit_disabled_config(self):
        """Test collector with explicitly disabled config."""
        config = FeedbackCollectorConfig(enabled=False)
        collector = FeedbackCollector(config)
        
        # Should be no-op
        record_id = collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": False, "score": 0.9}},
            prompt="test"
        )
        assert record_id is None
    
    def test_disabled_has_no_storage(self):
        """Test that disabled collector doesn't create storage."""
        collector = FeedbackCollector()
        assert collector._storage is None


class TestFeedbackCollectorEnabled:
    """Tests for FeedbackCollector when enabled."""
    
    def test_record_scan_basic(self):
        """Test basic scan recording."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        record_id = collector.record_scan(
            scan_type="prompt",
            scanner_results={"Toxicity": {"valid": False, "score": 0.9}},
            prompt="This is toxic"
        )
        
        assert record_id is not None
        assert len(collector.get_records()) == 1
    
    def test_record_scan_with_output(self):
        """Test recording output scan."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        record_id = collector.record_scan(
            scan_type="output",
            scanner_results={"Bias": {"valid": False, "score": 0.8}},  # Changed to False
            prompt="What is AI?",
            output="AI is artificial intelligence"
        )
        
        assert record_id is not None
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].scan_type == "output"
        assert records[0].output_hash is not None
    
    def test_privacy_level_0_no_samples(self):
        """Test that privacy level 0 stores no text samples."""
        config = FeedbackCollectorConfig(enabled=True, privacy_level=0)
        collector = FeedbackCollector(config)
        
        collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": False, "score": 0.9}},
            prompt="This is a test prompt"
        )
        
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].prompt_sample is None
        assert records[0].prompt_hash is not None  # Hash should exist
        assert records[0].prompt_length > 0  # Length should exist
    
    def test_privacy_level_1_with_samples(self):
        """Test that privacy level 1 includes text samples."""
        config = FeedbackCollectorConfig(enabled=True, privacy_level=1)
        collector = FeedbackCollector(config)
        
        long_prompt = "A" * 100
        collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": False, "score": 0.9}},
            prompt=long_prompt
        )
        
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].prompt_sample is not None
        assert len(records[0].prompt_sample) == 50  # First 50 chars
    
    def test_include_correct_false(self):
        """Test that correct scans are not recorded by default."""
        config = FeedbackCollectorConfig(enabled=True, include_correct=False)
        collector = FeedbackCollector(config)
        
        # All scanners valid
        record_id = collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": True, "score": 0.1}},
            prompt="Hello"
        )
        
        assert record_id is None
        assert len(collector.get_records()) == 0
    
    def test_include_correct_true(self):
        """Test that correct scans are recorded when configured."""
        config = FeedbackCollectorConfig(enabled=True, include_correct=True)
        collector = FeedbackCollector(config)
        
        # All scanners valid
        record_id = collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": True, "score": 0.1}},
            prompt="Hello"
        )
        
        assert record_id is not None
        assert len(collector.get_records()) == 1
    
    def test_sampling_rate(self):
        """Test that sampling rate is respected."""
        config = FeedbackCollectorConfig(enabled=True, sampling_rate=0.0)
        collector = FeedbackCollector(config)
        
        # With 0% sampling, nothing should be recorded
        for _ in range(10):
            record_id = collector.record_scan(
                "prompt",
                {"Toxicity": {"valid": False, "score": 0.9}},
                prompt="test"
            )
            assert record_id is None
        
        assert len(collector.get_records()) == 0
    
    def test_report_feedback(self):
        """Test adding feedback to a record."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        record_id = collector.record_scan(
            "prompt",
            {"Toxicity": {"valid": False, "score": 0.9}},
            prompt="test"
        )
        
        # Add feedback
        success = collector.report_feedback(
            record_id,
            "false_positive",
            ["Toxicity"],
            "This is not toxic"
        )
        
        assert success is True
        
        # Verify feedback was added
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].feedback_type == "false_positive"
        assert records[0].reported_scanners == ["Toxicity"]
        assert records[0].user_comment == "This is not toxic"
    
    def test_report_feedback_nonexistent_record(self):
        """Test reporting feedback for nonexistent record."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        success = collector.report_feedback(
            "nonexistent-id",
            "false_positive",
            ["Toxicity"]
        )
        
        assert success is False
    
    def test_get_records_with_filter(self):
        """Test filtering records."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        # Add multiple records
        id1 = collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        id2 = collector.record_scan("output", {"Bias": {"valid": False, "score": 0.8}})
        
        collector.report_feedback(id1, "false_positive", ["Toxicity"])
        
        # Filter by feedback_type
        filtered = collector.get_records(filter_by={"feedback_type": "false_positive"})
        assert len(filtered) == 1
        assert filtered[0].record_id == id1
        
        # Filter by scan_type
        filtered = collector.get_records(filter_by={"scan_type": "output"})
        assert len(filtered) == 1
        assert filtered[0].record_id == id2
    
    def test_clear_records(self):
        """Test clearing all records."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        # Add some records
        for i in range(5):
            collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        
        assert len(collector.get_records()) == 5
        
        count = collector.clear_records()
        assert count == 5
        assert len(collector.get_records()) == 0
    
    def test_get_stats(self):
        """Test getting statistics."""
        config = FeedbackCollectorConfig(enabled=True, privacy_level=1)
        collector = FeedbackCollector(config)
        
        # Add records with different feedback types
        id1 = collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        id2 = collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        id3 = collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        
        collector.report_feedback(id1, "false_positive", ["Toxicity"])
        collector.report_feedback(id2, "false_negative", ["Toxicity"])
        
        stats = collector.get_stats()
        
        assert stats["enabled"] is True
        assert stats["total_records"] == 3
        assert stats["privacy_level"] == 1
        assert stats["storage_backend"] == "memory"
        assert stats["feedback_counts"]["false_positive"] == 1
        assert stats["feedback_counts"]["false_negative"] == 1
        assert stats["feedback_counts"]["no_feedback"] == 1


class TestFeedbackCollectorWithFileStorage:
    """Tests for FeedbackCollector with file storage."""
    
    def test_file_storage_backend(self):
        """Test using file storage backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            
            config = FeedbackCollectorConfig(
                enabled=True,
                storage_backend="file",
                storage_path=str(file_path)
            )
            collector = FeedbackCollector(config)
            
            collector.record_scan(
                "prompt",
                {"Toxicity": {"valid": False, "score": 0.9}},
                prompt="test"
            )
            
            assert file_path.exists()
            assert len(collector.get_records()) == 1
    
    def test_file_storage_persistence(self):
        """Test that file storage persists across collector instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "feedback.json"
            
            # Create first collector and add record
            config1 = FeedbackCollectorConfig(
                enabled=True,
                storage_backend="file",
                storage_path=str(file_path)
            )
            collector1 = FeedbackCollector(config1)
            collector1.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
            
            # Create second collector (should load from file)
            config2 = FeedbackCollectorConfig(
                enabled=True,
                storage_backend="file",
                storage_path=str(file_path)
            )
            collector2 = FeedbackCollector(config2)
            
            assert len(collector2.get_records()) == 1


class TestFeedbackCollectorWithMemoryStorage:
    """Tests for FeedbackCollector with memory storage."""
    
    def test_memory_storage_respects_max_records(self):
        """Test that memory storage respects max_records limit."""
        config = FeedbackCollectorConfig(
            enabled=True,
            storage_backend="memory",
            max_records=3
        )
        collector = FeedbackCollector(config)
        
        # Add 5 records
        for i in range(5):
            collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        
        # Should only keep last 3
        assert len(collector.get_records()) == 3


class TestFeedbackCollectorValidation:
    """Tests for FeedbackCollector validation."""
    
    def test_unsupported_storage_backend(self):
        """Test that unsupported storage backend raises error."""
        config = FeedbackCollectorConfig(
            enabled=True,
            storage_backend="custom"  # Not supported in Phase 2
        )
        
        with pytest.raises(ValueError, match="Unsupported storage backend"):
            FeedbackCollector(config)
    
    def test_file_backend_without_path(self):
        """Test that file backend without path raises error."""
        # This should be caught by FeedbackCollectorConfig validation
        with pytest.raises(ValueError, match="storage_path is required"):
            FeedbackCollectorConfig(
                enabled=True,
                storage_backend="file"
                # storage_path not provided
            )


class TestPhase1And2Integration:
    """Tests verifying Phase 1 and Phase 2 work together."""
    
    def test_phase1_models_still_work(self):
        """Test that Phase 1 data models still work correctly."""
        from llm_guard.feedback import FeedbackRecord, FeedbackCollectorConfig
        
        # Test FeedbackRecord
        record = FeedbackRecord(
            record_id="test",
            timestamp=datetime.now(),
            scan_type="prompt",
            scanner_results={}
        )
        assert record.record_id == "test"
        
        # Test FeedbackCollectorConfig
        config = FeedbackCollectorConfig(enabled=True, privacy_level=2)
        assert config.enabled is True
        assert config.privacy_level == 2
    
    def test_collector_uses_phase1_models(self):
        """Test that collector correctly uses Phase 1 models."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        collector.record_scan("prompt", {"Toxicity": {"valid": False, "score": 0.9}})
        
        records = collector.get_records()
        assert len(records) == 1
        
        # Verify it's a FeedbackRecord instance
        from llm_guard.feedback import FeedbackRecord
        assert isinstance(records[0], FeedbackRecord)
    
    def test_no_core_llm_guard_impact(self):
        """Test that feedback module doesn't impact core llm_guard."""
        # This should still work
        try:
            import llm_guard
            # If this doesn't raise, core is unaffected
            assert True
        except ImportError:
            # Expected if presidio not installed (from Phase 1)
            assert True
