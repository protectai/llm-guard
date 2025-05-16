import pytest

from llm_guard.input_scanners.regex import MatchType, Regex


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a prompt", "Just a prompt", True, -1.0),  # Correct output
        (
            "Here is my token: Bearer abc-def_123",
            "Here is my token: [REDACTED]",
            False,
            1.0,
        ),  # Regex matched
        (
            "What is 12345? 12345",
            "What is [REDACTED]? [REDACTED]",
            False,
            1.0,
        ),  # Multiple matches
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Regex(
        patterns=[r"Bearer [A-Za-z0-9-._~+/]+", r"\d{5}"],
        match_type=MatchType.ALL,
        is_blocked=True,
        redact=True,
    )
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
