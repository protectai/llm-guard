import pytest

from llm_guard.input_scanners.emotion_detection import EmotionDetection


@pytest.mark.parametrize(
    "prompt,expected_valid,check_score",
    [
        ("Just a simple prompt", True, lambda s: s == 0.0),  # Simple prompt
        ("I am so happy today!", True, lambda s: s == 0.0),  # Positive emotion (not blocked)
        ("I am so angry right now!", False, lambda s: s > 0.0),  # Blocked emotion
        ("This makes me feel disgusted", False, lambda s: s > 0.0),  # Blocked emotion
        ("I am feeling sad about this", False, lambda s: s > 0.0),  # Blocked emotion
        ("I am nervous about the test", False, lambda s: s > 0.0),  # Blocked emotion
        ("", True, lambda s: s == -1.0),  # Empty prompt
    ],
)
def test_scan(prompt, expected_valid, check_score):
    scanner = EmotionDetection(
        threshold=0.5, blocked_emotions=["anger", "disgust", "sadness", "nervousness"]
    )
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert check_score(score), f"Score {score} failed check for prompt: {prompt}"


def test_scan_default_blocked_emotions():
    """Test that the scanner uses default blocked emotions when none specified."""
    scanner = EmotionDetection(threshold=0.5)
    # Should block negative emotions by default
    prompt = "I am so angry and sad about this situation!"
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == False  # Should be blocked due to anger and sadness
    assert score > 0.0


def test_scan_custom_blocked_emotions():
    """Test that the scanner can use custom blocked emotions."""
    scanner = EmotionDetection(
        threshold=0.5,
        blocked_emotions=["joy", "love"],  # Block positive emotions
    )
    prompt = "I am so happy and in love!"
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == False  # Should be blocked due to joy and love
    assert score > 0.0


def test_scan_no_blocked_emotions():
    """Test that the scanner allows all emotions when blocked_emotions is empty."""
    scanner = EmotionDetection(
        threshold=0.5,
        blocked_emotions=[],  # No blocked emotions
    )
    prompt = "I am so angry and sad about this situation!"
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == True  # Should be allowed since no emotions are blocked
    assert score == 0.0


def test_get_emotion_analysis():
    """Test that the scanner can return full emotion analysis."""
    scanner = EmotionDetection(threshold=0.5)
    prompt = "I am so happy and excited about this!"

    emotion_analysis = scanner.get_emotion_analysis(prompt)
    assert isinstance(emotion_analysis, dict)
    # Should contain emotion scores
    assert len(emotion_analysis) > 0


def test_scan_with_full_output():
    """Test that the scanner can return full output with emotion analysis."""
    scanner = EmotionDetection(threshold=0.5, return_full_output=True)
    prompt = "I am so angry about this situation!"

    sanitized_prompt, valid, score, emotion_analysis = scanner.scan_with_full_output(prompt)
    assert sanitized_prompt == prompt
    assert valid == False  # Should be blocked due to anger
    assert score > 0.0
    assert isinstance(emotion_analysis, dict)
    assert len(emotion_analysis) > 0


def test_scan_with_full_output_mode():
    """Test that the scanner works in full output mode."""
    scanner = EmotionDetection(threshold=0.5, return_full_output=True)
    prompt = "I am so happy and excited about this!"

    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == True  # Should be allowed since happiness is not blocked by default
    assert score == 0.0
    # Check that emotion analysis was stored
    assert hasattr(scanner, "_last_emotion_analysis")
