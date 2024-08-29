import pytest

from llm_guard.output_scanners.sensitive import Sensitive


@pytest.mark.parametrize(
    "output,expected_output,expected_valid,expected_score",
    [
        (
            "Sorry, I can't",
            "Sorry, I can't",
            True,
            -1.0,
        ),  # No sensitive information
        (
            "john.doe@protectai.com is my email",
            "<EMAIL_ADDRESS> is my email",
            False,
            1.0,
        ),  # Name in the output
    ],
)
def test_scan(output, expected_output, expected_valid, expected_score):
    scanner = Sensitive(redact=True, entity_types=["EMAIL_ADDRESS", "EMAIL_ADDRESS_RE"])
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
