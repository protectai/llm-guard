import pytest

from llm_guard.input_scanners.language import Language


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a prompt", "Just a prompt", True, 0.0),  # Correct output
        ("Me llamo Sofía", "Me llamo Sofía", False, 1.0),  # Spanish
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Language(valid_languages=["en"])
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
