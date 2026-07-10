"""
Tests for feedback data models.

These tests verify dataclass instantiation, default values, and validation logic.
No runtime behavior or integration testing is included in Phase 1.
"""

from datetime import datetime

import pytest

from llm_guard.feedback.model import FeedbackCollectorConfig, FeedbackRecord


class TestFeedbackRecord:
    """Tests for FeedbackRecord dataclass."""

    def test_minimal_instantiation(self):
        """Test creating a FeedbackRecord with only required fields."""
        record = FeedbackRecord(
            record_id="test-123",
            timestamp=datetime.now(),
            scan_type="prompt",
            scanner_results={"Toxicity": {"valid": True, "score": 0.1}},
        )

        assert record.record_id == "test-123"
        assert record.scan_type == "prompt"
        assert record.scanner_results == {"Toxicity": {"valid": True, "score": 0.1}}

        # Verify defaults
        assert record.feedback_type is None
        assert record.reported_scanners == []
        assert record.user_comment is None
        assert record.prompt_hash is None
        assert record.output_hash is None
        assert record.prompt_length == 0
        assert record.output_length is None
        assert record.scanner_versions == {}
        assert record.llm_guard_version == ""
        assert record.prompt_sample is None
        assert record.output_sample is None

    def test_full_instantiation(self):
        """Test creating a FeedbackRecord with all fields populated."""
        now = datetime.now()
        record = FeedbackRecord(
            record_id="test-456",
            timestamp=now,
            scan_type="output",
            scanner_results={
                "Toxicity": {"valid": False, "score": 0.9},
                "Bias": {"valid": True, "score": 0.2},
            },
            feedback_type="false_positive",
            reported_scanners=["Toxicity"],
            user_comment="This is not toxic",
            prompt_hash="abc123",
            output_hash="def456",
            prompt_length=50,
            output_length=100,
            scanner_versions={"Toxicity": "1.0.0", "Bias": "1.0.0"},
            llm_guard_version="0.3.16",
            prompt_sample="Sample prompt...",
            output_sample="Sample output...",
        )

        assert record.record_id == "test-456"
        assert record.timestamp == now
        assert record.scan_type == "output"
        assert record.feedback_type == "false_positive"
        assert record.reported_scanners == ["Toxicity"]
        assert record.user_comment == "This is not toxic"
        assert record.prompt_hash == "abc123"
        assert record.output_hash == "def456"
        assert record.prompt_length == 50
        assert record.output_length == 100
        assert record.scanner_versions == {"Toxicity": "1.0.0", "Bias": "1.0.0"}
        assert record.llm_guard_version == "0.3.16"
        assert record.prompt_sample == "Sample prompt..."
        assert record.output_sample == "Sample output..."

    def test_scan_type_values(self):
        """Test that scan_type accepts valid literal values."""
        prompt_record = FeedbackRecord(
            record_id="test-1",
            timestamp=datetime.now(),
            scan_type="prompt",
            scanner_results={},
        )
        assert prompt_record.scan_type == "prompt"

        output_record = FeedbackRecord(
            record_id="test-2",
            timestamp=datetime.now(),
            scan_type="output",
            scanner_results={},
        )
        assert output_record.scan_type == "output"

    def test_feedback_type_values(self):
        """Test that feedback_type accepts valid literal values."""
        for feedback_type in ["false_positive", "false_negative", "correct"]:
            record = FeedbackRecord(
                record_id=f"test-{feedback_type}",
                timestamp=datetime.now(),
                scan_type="prompt",
                scanner_results={},
                feedback_type=feedback_type,
            )
            assert record.feedback_type == feedback_type


class TestFeedbackCollectorConfig:
    """Tests for FeedbackCollectorConfig dataclass."""

    def test_default_instantiation(self):
        """Test creating a config with all defaults."""
        config = FeedbackCollectorConfig()

        assert config.enabled is False
        assert config.privacy_level == 0
        assert config.storage_backend == "memory"
        assert config.storage_path is None
        assert config.max_records == 1000
        assert config.sampling_rate == 1.0
        assert config.include_correct is False
        assert config.auto_flush is False

    def test_custom_instantiation(self):
        """Test creating a config with custom values."""
        config = FeedbackCollectorConfig(
            enabled=True,
            privacy_level=2,
            storage_backend="file",
            storage_path="/tmp/feedback.json",
            max_records=500,
            sampling_rate=0.5,
            include_correct=True,
            auto_flush=True,
        )

        assert config.enabled is True
        assert config.privacy_level == 2
        assert config.storage_backend == "file"
        assert config.storage_path == "/tmp/feedback.json"
        assert config.max_records == 500
        assert config.sampling_rate == 0.5
        assert config.include_correct is True
        assert config.auto_flush is True

    def test_privacy_level_validation(self):
        """Test that privacy_level is validated to be 0-3."""
        # Valid values
        for level in [0, 1, 2, 3]:
            config = FeedbackCollectorConfig(privacy_level=level)
            assert config.privacy_level == level

        # Invalid values
        with pytest.raises(ValueError, match="privacy_level must be 0-3"):
            FeedbackCollectorConfig(privacy_level=-1)

        with pytest.raises(ValueError, match="privacy_level must be 0-3"):
            FeedbackCollectorConfig(privacy_level=4)

    def test_sampling_rate_validation(self):
        """Test that sampling_rate is validated to be 0.0-1.0."""
        # Valid values
        for rate in [0.0, 0.5, 1.0]:
            config = FeedbackCollectorConfig(sampling_rate=rate)
            assert config.sampling_rate == rate

        # Invalid values
        with pytest.raises(ValueError, match="sampling_rate must be 0.0-1.0"):
            FeedbackCollectorConfig(sampling_rate=-0.1)

        with pytest.raises(ValueError, match="sampling_rate must be 0.0-1.0"):
            FeedbackCollectorConfig(sampling_rate=1.5)

    def test_max_records_validation(self):
        """Test that max_records must be >= 1."""
        # Valid value
        config = FeedbackCollectorConfig(max_records=1)
        assert config.max_records == 1

        # Invalid value
        with pytest.raises(ValueError, match="max_records must be >= 1"):
            FeedbackCollectorConfig(max_records=0)

        with pytest.raises(ValueError, match="max_records must be >= 1"):
            FeedbackCollectorConfig(max_records=-10)

    def test_file_backend_requires_path(self):
        """Test that storage_backend='file' requires storage_path."""
        # Valid: file backend with path
        config = FeedbackCollectorConfig(storage_backend="file", storage_path="/tmp/feedback.json")
        assert config.storage_backend == "file"
        assert config.storage_path == "/tmp/feedback.json"

        # Invalid: file backend without path
        with pytest.raises(ValueError, match="storage_path is required"):
            FeedbackCollectorConfig(storage_backend="file")

    def test_auto_flush_requires_file_backend(self):
        """Test that auto_flush requires storage_backend='file'."""
        # Valid: auto_flush with file backend
        config = FeedbackCollectorConfig(
            storage_backend="file", storage_path="/tmp/feedback.json", auto_flush=True
        )
        assert config.auto_flush is True

        # Invalid: auto_flush with memory backend
        with pytest.raises(ValueError, match="auto_flush requires storage_backend='file'"):
            FeedbackCollectorConfig(storage_backend="memory", auto_flush=True)

    def test_storage_backend_values(self):
        """Test that storage_backend accepts valid literal values."""
        for backend in ["memory", "file", "custom"]:
            if backend == "file":
                config = FeedbackCollectorConfig(
                    storage_backend=backend, storage_path="/tmp/test.json"
                )
            else:
                config = FeedbackCollectorConfig(storage_backend=backend)
            assert config.storage_backend == backend
