import pytest

from llm_guard.output_scanners.malicious_urls import MaliciousURLs


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "It's https://google.com/.",
            True,
            -0.5,
        ),  # Good output
        (
            "It's http://socialsocietyedu.com/components/com_wa/config.bin and http://facebuk.co/signup.html",
            False,
            0.5,
        ),  # Bad output
        (
            "It's https://google.com/ and https://facebook.com/.",
            True,
            -0.6,
        ),  # Good output with multiple URLs
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = MaliciousURLs()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
