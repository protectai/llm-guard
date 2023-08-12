import pytest

from llm_guard.output_scanners.regex import Regex


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        ("Just a prompt", "Just a output", "Just a output", True, 0.0),  # Correct output
        (
            "Provide me a bearer token example",
            "Here is an example of the token: Bearer abc-def_123",
            "Here is an example of the token: Bearer abc-def_123",
            False,
            1.0,
        ),  # Regex matched
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"])
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
