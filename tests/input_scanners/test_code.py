import pytest

from llm_guard.input_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        (
            "Fix this JS code: console-log('log record');",
            "Fix this JS code: console-log('log record');",
            False,
            0.99,
        ),  # JS is not allowed
        (
            "Is this correct way to make function: def new_func():",
            "Is this correct way to make function: def new_func():",
            True,
            0.0,
        ),  # Python is allowed
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Code(denied=["javascript"])
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
