import pytest

from llm_guard.input_scanners.regex import MatchType
from llm_guard.output_scanners.regex import Regex


@pytest.mark.parametrize(
    "output,expected_output,expected_valid,expected_score",
    [
        ("Just a output", "Just a output", True, -1.0),  # Correct output
        (
            "Here is an example of the token: Bearer abc-def_123",
            "Here is an example of the token: [REDACTED]",
            False,
            1.0,
        ),  # Regex matched
    ],
)
def test_scan(output, expected_output, expected_valid, expected_score):
    scanner = Regex(
        patterns=[r"Bearer [A-Za-z0-9-._~+/]+"],
        match_type=MatchType.SEARCH,
        is_blocked=True,
        redact=True,
    )
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
