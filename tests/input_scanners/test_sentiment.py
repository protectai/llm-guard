import pytest

from llm_guard.input_scanners.sentiment import Sentiment


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        ("Just a simple prompt", "Just a simple prompt", True),  # Simple prompt
        (
            "I heard that Mars is the closest planet to Earth. Is that true?",
            "I heard that Mars is the closest planet to Earth. Is that true?",
            True,
        ),  # Positive sentiment
        (
            "I am so upset right now. My flight was canceled and I have been stuck at the airport for hours with no "
            "information. The airline's customer service has been terrible. I just can't believe this. Isn't this a "
            "terrible situation?",
            "I am so upset right now. My flight was canceled and I have been stuck at the airport for hours with no "
            "information. The airline's customer service has been terrible. I just can't believe this. Isn't this a "
            "terrible situation?",
            False,
        ),  # Negative sentiment
        ("I'm sick of these", "I'm sick of these", False),
        (
            "Dude, it's really not cool to call a person a wo",
            "Dude, it's really not cool to call a person a wo",
            False,
        ),
        ("", "", True),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = Sentiment()
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
