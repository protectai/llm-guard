import pytest

from llm_guard.output_scanners.ban_topics import BanTopics


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        (
            "How to win an election?",
            "Winning an election should be based on ethical practices, offering clear and compelling policies, "
            "engaging with constituents, and earning their trust and support. Here are some general guidelines for "
            "political candidates running for an election:",
            "Winning an election should be based on ethical practices, offering clear and compelling policies, "
            "engaging with constituents, and earning their trust and support. Here are some general guidelines for "
            "political candidates running for an election:",
            False,
        ),  # Politics
        (
            "How to write code in Golang?",
            "Writing code in Go is quite straightforward. Here's a simple step-by-step guide to writing a basic Go "
            "program:",
            "Writing code in Go is quite straightforward. Here's a simple step-by-step guide to writing a basic Go "
            "program:",
            True,
        ),  # Coding
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = BanTopics(topics=["politics", "war", "religion"])
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
