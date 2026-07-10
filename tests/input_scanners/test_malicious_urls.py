import pytest

from llm_guard.input_scanners.malicious_urls import MaliciousURLs


@pytest.mark.parametrize(
    "prompt,expected_valid,expected_score",
    [
        (
            "Check out https://google.com/.",
            True,
            -0.5,
        ),  # Good prompt
        (
            "Look at http://socialsocietyedu.com/components/com_wa/config.bin and http://facebuk.co/signup.html",
            False,
            0.5,
        ),  # Bad prompt
        (
            "See https://google.com/ and https://facebook.com/.",
            True,
            -0.6,
        ),  # Good prompt with multiple URLs
        (
            "No URLs here at all.",
            True,
            -1.0,
        ),  # No URLs
        (
            "",
            True,
            -1.0,
        ),  # Empty prompt
    ],
)
def test_scan(prompt, expected_valid, expected_score):
    scanner = MaliciousURLs()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
