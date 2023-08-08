import pytest

from llm_guard.output_scanners.regex import Regex


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        ("Just a prompt", "Just a output", "Just a output", True),  # Correct output
        (
            "Provide me a bearer token example",
            "Here is an example of the token: Bearer abc-def_123",
            "Here is an example of the token: Bearer abc-def_123",
            False,
        ),  # Regex matched
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"])
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
