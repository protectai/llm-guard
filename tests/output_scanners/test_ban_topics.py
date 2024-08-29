import pytest

from llm_guard.output_scanners.ban_topics import BanTopics


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "Winning an election should be based on ethical practices, offering clear and compelling policies, "
            "engaging with constituents, and earning their trust and support. Here are some general guidelines for "
            "political candidates running for an election:",
            False,
            1.0,
        ),  # Politics
        (
            "Writing code in Go is quite straightforward. Here's a simple step-by-step guide to writing a basic Go "
            "program:",
            True,
            -0.3,
        ),  # Coding
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = BanTopics(topics=["politics", "war", "religion"])
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
