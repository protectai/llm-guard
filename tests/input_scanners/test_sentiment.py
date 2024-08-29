import pytest

from llm_guard.input_scanners.sentiment import Sentiment


@pytest.mark.parametrize(
    "prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", True, 0.0),  # Simple prompt
        (
            "I heard that Mars is the closest planet to Earth. Is that true?",
            True,
            0.0,
        ),  # Positive sentiment
        (
            "I am so upset right now. My flight was canceled and I have been stuck at the airport for hours with no "
            "information. The airline's customer service has been terrible. I just can't believe this. Isn't this a "
            "terrible situation?",
            False,
            0.9,
        ),  # Negative sentiment
        ("I'm sick of these", False, 0.6),  # Negative sentiment
        (
            "Dude, it's really not cool to call a person a wo",
            False,
            0.5,
        ),  # Negative sentiment
        ("", True, -1.0),  # Empty prompt
    ],
)
def test_scan(prompt, expected_valid, expected_score):
    scanner = Sentiment()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
