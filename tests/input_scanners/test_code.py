import pytest

from llm_guard.input_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        ("Just a simple prompt", "Just a simple prompt", True),  # Simple prompt
        (
            "Fix this JS code: console-log('log record');",
            "Fix this JS code: console-log('log record');",
            False,
        ),  # JS is not allowed
        (
            "Is this correct way to make function def new_func():",
            "Is this correct way to make function def new_func():",
            True,
        ),
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = Code(denied=["javascript"])
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
