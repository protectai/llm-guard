import pytest

from llm_guard.output_scanners.sentiment import Sentiment


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "I don't have a specific answer for you but I will try to help",
            True,
            0.0,
        ),  # No negative sentiment
        (
            "I'm sick of your prompts",
            False,
            0.6,
        ),  # Negative sentiment
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = Sentiment()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
