import pytest

from llm_guard.output_scanners.emotion_detection import EmotionDetection


@pytest.mark.parametrize(
    "output,expected_valid,check_score",
    [
        (
            "I don't have a specific answer for you but I will try to help",
            True,
            lambda s: s == 0.0,
        ),  # No blocked emotions
        (
            "I am so angry about this situation!",
            False,
            lambda s: s > 0.0,
        ),  # Blocked emotion
        (
            "I am feeling sad and disappointed",
            False,
            lambda s: s > 0.0,
        ),  # Blocked emotions
        (
            "I am so happy to help you!",
            True,
            lambda s: s == 0.0,
        ),  # Positive emotion (not blocked)
    ],
)
def test_scan(output, expected_valid, check_score):
    scanner = EmotionDetection(
        threshold=0.5, blocked_emotions=["anger", "sadness", "disappointment"]
    )
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert check_score(score), f"Score {score} failed check for output: {output}"


def test_scan_default_blocked_emotions():
    """Test that the scanner uses default blocked emotions when none specified."""
    scanner = EmotionDetection(threshold=0.5)
    # Should block negative emotions by default
    output = "I am so angry and sad about this situation!"
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == False  # Should be blocked due to anger and sadness
    assert score > 0.0


def test_scan_custom_blocked_emotions():
    """Test that the scanner can use custom blocked emotions."""
    scanner = EmotionDetection(
        threshold=0.5,
        blocked_emotions=["joy", "love"],  # Block positive emotions
    )
    output = "I am so happy and in love!"
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == False  # Should be blocked due to joy and love
    assert score > 0.0


def test_get_emotion_analysis():
    """Test that the scanner can return full emotion analysis."""
    scanner = EmotionDetection(threshold=0.5)
    output = "I am so happy and excited to help you!"

    emotion_analysis = scanner.get_emotion_analysis(output)
    assert isinstance(emotion_analysis, dict)
    # Should contain emotion scores
    assert len(emotion_analysis) > 0


def test_scan_with_full_output():
    """Test that the scanner can return full output with emotion analysis."""
    scanner = EmotionDetection(threshold=0.5, return_full_output=True)
    output = "I am so angry about this situation!"

    sanitized_output, valid, score, emotion_analysis = scanner.scan_with_full_output("", output)
    assert sanitized_output == output
    assert valid == False  # Should be blocked due to anger
    assert score > 0.0
    assert isinstance(emotion_analysis, dict)
    assert len(emotion_analysis) > 0
