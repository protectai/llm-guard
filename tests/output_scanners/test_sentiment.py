import pytest

from llm_guard.output_scanners.sentiment import Sentiment


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "What is the closes plannet to the Earth?",
            "I don't have a specific answer for you but I will try to help",
            "I don't have a specific answer for you but I will try to help",
            True,
            0.0,
        ),  # No negative sentiment
        (
            "Tell me something negative",
            "I'm sick of your prompts",
            "I'm sick of your prompts",
            False,
            0.54,
        ),  # Negative sentiment
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Sentiment()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
