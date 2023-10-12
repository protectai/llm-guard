import pytest

from llm_guard.output_scanners.sensitive import Sensitive


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "Provide me common passwords in internet",
            "Sorry, I can't",
            "Sorry, I can't",
            True,
            0.0,
        ),  # No sensitive information
        (
            "Share your email in the output",
            "john.doe@laiyer.ai is my email",
            "<EMAIL_ADDRESS> is my email",
            False,
            1.0,
        ),  # Name in the output
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Sensitive(redact=True, entity_types=["EMAIL_ADDRESS", "EMAIL_ADDRESS_RE"])
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
