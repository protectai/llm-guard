import pytest

from llm_guard.output_scanners.malicious_urls import MaliciousURLs


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "What is the most popular website?",
            "It's https://google.com/.",
            "It's https://google.com/.",
            True,
            0.0,
        ),  # Good output
        (
            "What is the most popular website?",
            "It's http://www.marketingbyinternet.com/mo/e56508df639f6ce7d55c81ee3fcd5ba8/",
            "It's http://www.marketingbyinternet.com/mo/e56508df639f6ce7d55c81ee3fcd5ba8/",
            False,
            1.0,
        ),  # Bad output
        (
            "What is the most popular website?",
            "It's https://google.com/ and https://facebook.com/.",
            "It's https://google.com/ and https://facebook.com/.",
            True,
            0.0,
        ),  # Good output with multiple URLs
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = MaliciousURLs()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
