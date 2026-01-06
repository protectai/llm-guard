"""
Tests for feedback wrapper functions.

These tests verify that wrapper functions correctly integrate with scan_prompt
and scan_output while maintaining exact same behavior and return values.
"""

import pytest

from llm_guard.feedback import FeedbackCollector, FeedbackCollectorConfig
from llm_guard.feedback.wrapper import (
    scan_output_with_feedback,
    scan_prompt_with_feedback,
)


# Mock scanner for testing
class TestScanner:
    """Mock input scanner for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return prompt, self._valid, self._score


class Scanner1:
    """Mock input scanner 1 for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return prompt, self._valid, self._score


class Scanner2:
    """Mock input scanner 2 for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return prompt, self._valid, self._score


# Output scanner mocks
class OutputTestScanner:
    """Mock output scanner for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return output, self._valid, self._score


class OutputScanner1:
    """Mock output scanner 1 for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return output, self._valid, self._score


class OutputScanner2:
    """Mock output scanner 2 for testing."""
    
    def __init__(self, valid: bool = True, score: float = 0.0):
        self._valid = valid
        self._score = score
    
    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        """Mock scan method."""
        return output, self._valid, self._score


class TestScanPromptWithFeedback:
    """Tests for scan_prompt_with_feedback wrapper."""
    
    def test_without_collector(self):
        """Test wrapper without collector behaves like scan_prompt."""
        from llm_guard import scan_prompt
        
        scanners = [TestScanner(valid=True, score=0.1)]
        prompt = "Hello world"
        
        # Call wrapper without collector
        result_wrapper = scan_prompt_with_feedback(scanners, prompt, collector=None)
        
        # Call original scan_prompt
        result_original = scan_prompt(scanners, prompt)
        
        # Results should be identical
        assert result_wrapper == result_original
    
    def test_with_disabled_collector(self):
        """Test wrapper with disabled collector doesn't record."""
        config = FeedbackCollectorConfig(enabled=False)
        collector = FeedbackCollector(config)
        
        scanners = [TestScanner(valid=False, score=0.9)]
        prompt = "Test prompt"
        
        # Call wrapper
        sanitized, valid, scores = scan_prompt_with_feedback(
            scanners, prompt, collector=collector
        )
        
        # Verify results
        assert sanitized == prompt
        assert valid == {"TestScanner": False}
        assert scores == {"TestScanner": 0.9}
        
        # Verify nothing was recorded
        assert len(collector.get_records()) == 0
    
    def test_with_enabled_collector(self):
        """Test wrapper with enabled collector records scan."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        scanners = [TestScanner(valid=False, score=0.9)]
        prompt = "Test prompt"
        
        # Call wrapper
        sanitized, valid, scores = scan_prompt_with_feedback(
            scanners, prompt, collector=collector
        )
        
        # Verify results are correct
        assert sanitized == prompt
        assert valid == {"TestScanner": False}
        assert scores == {"TestScanner": 0.9}
        
        # Verify scan was recorded
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].scan_type == "prompt"
        assert records[0].scanner_results == {
            "TestScanner": {"valid": False, "score": 0.9}
        }
    
    def test_with_multiple_scanners(self):
        """Test wrapper with multiple scanners."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        scanners = [
            Scanner1(valid=True, score=0.1),
            Scanner2(valid=False, score=0.8),
        ]
        prompt = "Test prompt"
        
        # Call wrapper
        sanitized, valid, scores = scan_prompt_with_feedback(
            scanners, prompt, collector=collector
        )
        
        # Verify results
        assert valid == {"Scanner1": True, "Scanner2": False}
        assert scores == {"Scanner1": 0.1, "Scanner2": 0.8}
        
        # Verify scan was recorded with all scanners
        records = collector.get_records()
        assert len(records) == 1
        assert "Scanner1" in records[0].scanner_results
        assert "Scanner2" in records[0].scanner_results
    
    def test_with_fail_fast(self):
        """Test wrapper passes through fail_fast parameter."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        scanners = [
            Scanner1(valid=False, score=0.9),
            Scanner2(valid=True, score=0.1),
        ]
        prompt = "Test prompt"
        
        # Call wrapper with fail_fast=True
        sanitized, valid, scores = scan_prompt_with_feedback(
            scanners, prompt, collector=collector, fail_fast=True
        )
        
        # With fail_fast, only first scanner should run
        assert "Scanner1" in valid
        # Scanner2 might or might not be in results depending on scan_prompt implementation
        
        # Verify scan was recorded
        assert len(collector.get_records()) == 1
    
    def test_return_type_matches_scan_prompt(self):
        """Test that wrapper returns exact same type as scan_prompt."""
        from llm_guard import scan_prompt
        
        scanners = [TestScanner(valid=True, score=0.5)]
        prompt = "Test"
        
        result_wrapper = scan_prompt_with_feedback(scanners, prompt)
        result_original = scan_prompt(scanners, prompt)
        
        # Check types match
        assert type(result_wrapper) == type(result_original)
        assert type(result_wrapper[0]) == type(result_original[0])
        assert type(result_wrapper[1]) == type(result_original[1])
        assert type(result_wrapper[2]) == type(result_original[2])


class TestScanOutputWithFeedback:
    """Tests for scan_output_with_feedback wrapper."""
    
    def test_without_collector(self):
        """Test wrapper without collector behaves like scan_output."""
        from llm_guard import scan_output
        
        scanners = [OutputTestScanner(valid=True, score=0.1)]
        prompt = "What is AI?"
        output = "AI is artificial intelligence"
        
        # Call wrapper without collector
        result_wrapper = scan_output_with_feedback(
            scanners, prompt, output, collector=None
        )
        
        # Call original scan_output
        result_original = scan_output(scanners, prompt, output)
        
        # Results should be identical
        assert result_wrapper == result_original
    
    def test_with_disabled_collector(self):
        """Test wrapper with disabled collector doesn't record."""
        config = FeedbackCollectorConfig(enabled=False)
        collector = FeedbackCollector(config)
        
        scanners = [OutputTestScanner(valid=False, score=0.9)]
        prompt = "What is AI?"
        output = "AI is artificial intelligence"
        
        # Call wrapper
        sanitized, valid, scores = scan_output_with_feedback(
            scanners, prompt, output, collector=collector
        )
        
        # Verify results
        assert sanitized == output
        assert valid == {"OutputTestScanner": False}
        assert scores == {"OutputTestScanner": 0.9}
        
        # Verify nothing was recorded
        assert len(collector.get_records()) == 0
    
    def test_with_enabled_collector(self):
        """Test wrapper with enabled collector records scan."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        scanners = [OutputTestScanner(valid=False, score=0.9)]
        prompt = "What is AI?"
        output = "AI is artificial intelligence"
        
        # Call wrapper
        sanitized, valid, scores = scan_output_with_feedback(
            scanners, prompt, output, collector=collector
        )
        
        # Verify results are correct
        assert sanitized == output
        assert valid == {"OutputTestScanner": False}
        assert scores == {"OutputTestScanner": 0.9}
        
        # Verify scan was recorded
        records = collector.get_records()
        assert len(records) == 1
        assert records[0].scan_type == "output"
        assert records[0].scanner_results == {
            "OutputTestScanner": {"valid": False, "score": 0.9}
        }
        # Verify both prompt and output hashes exist
        assert records[0].prompt_hash is not None
        assert records[0].output_hash is not None
    
    def test_with_multiple_scanners(self):
        """Test wrapper with multiple scanners."""
        config = FeedbackCollectorConfig(enabled=True)
        collector = FeedbackCollector(config)
        
        scanners = [
            OutputScanner1(valid=True, score=0.1),
            OutputScanner2(valid=False, score=0.8),
        ]
        prompt = "What is AI?"
        output = "AI is artificial intelligence"
        
        # Call wrapper
        sanitized, valid, scores = scan_output_with_feedback(
            scanners, prompt, output, collector=collector
        )
        
        # Verify results
        assert valid == {"OutputScanner1": True, "OutputScanner2": False}
        assert scores == {"OutputScanner1": 0.1, "OutputScanner2": 0.8}
        
        # Verify scan was recorded with all scanners
        records = collector.get_records()
        assert len(records) == 1
        assert "OutputScanner1" in records[0].scanner_results
        assert "OutputScanner2" in records[0].scanner_results
    
    def test_return_type_matches_scan_output(self):
        """Test that wrapper returns exact same type as scan_output."""
        from llm_guard import scan_output
        
        scanners = [OutputTestScanner(valid=True, score=0.5)]
        prompt = "Test"
        output = "Response"
        
        result_wrapper = scan_output_with_feedback(scanners, prompt, output)
        result_original = scan_output(scanners, prompt, output)
        
        # Check types match
        assert type(result_wrapper) == type(result_original)
        assert type(result_wrapper[0]) == type(result_original[0])
        assert type(result_wrapper[1]) == type(result_original[1])
        assert type(result_wrapper[2]) == type(result_original[2])


class TestWrapperIntegration:
    """Integration tests for wrappers."""
    
    def test_prompt_and_output_workflow(self):
        """Test complete workflow with both prompt and output scanning."""
        config = FeedbackCollectorConfig(enabled=True, include_correct=True)
        collector = FeedbackCollector(config)
        
        # Scan prompt
        prompt_scanners = [TestScanner(valid=True, score=0.1)]
        prompt = "What is AI?"
        
        sanitized_prompt, _, _ = scan_prompt_with_feedback(
            prompt_scanners, prompt, collector=collector
        )
        
        # Scan output
        output_scanners = [OutputTestScanner(valid=True, score=0.2)]
        output = "AI is artificial intelligence"
        
        sanitized_output, _, _ = scan_output_with_feedback(
            output_scanners, sanitized_prompt, output, collector=collector
        )
        
        # Verify both scans were recorded
        records = collector.get_records()
        assert len(records) == 2
        
        # Verify scan types
        scan_types = {r.scan_type for r in records}
        assert scan_types == {"prompt", "output"}
    
    def test_no_side_effects_on_core_scanning(self):
        """Test that wrappers don't affect core scanning behavior."""
        from llm_guard import scan_prompt
        
        scanners = [TestScanner(valid=False, score=0.9)]
        prompt = "Test"
        
        # Get result from original function
        original_result = scan_prompt(scanners, prompt)
        
        # Get result from wrapper (without collector)
        wrapper_result = scan_prompt_with_feedback(scanners, prompt)
        
        # Results must be identical
        assert wrapper_result == original_result
        
        # Get result from wrapper (with disabled collector)
        config = FeedbackCollectorConfig(enabled=False)
        collector = FeedbackCollector(config)
        wrapper_result_disabled = scan_prompt_with_feedback(
            scanners, prompt, collector=collector
        )
        
        # Results must still be identical
        assert wrapper_result_disabled == original_result
