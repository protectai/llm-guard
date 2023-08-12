import pytest

from llm_guard.input_scanners.secrets import Secrets


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            "Just a simple prompt",
            "Just a simple prompt",
            True,
            0.0,
        ),  # Prompt without sensitive data
        (
            'I need to pass a key\naws_secret_access_key="W/..py"',
            'I need to pass a key\naws_secret_access_key="******"',
            False,
            1.0,
        ),  # Prompt with a key
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Secrets()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
