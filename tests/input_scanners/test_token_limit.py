import pytest

from llm_guard.input_scanners.token_limit import TokenLimit


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        ("Just a simple prompt", "Just a simple prompt", True),  # Simple prompt
        (
            "Can you provide a comprehensive overview of the history of artificial intelligence? I'd like to understand "
            "its origins, major milestones, important figures, and current state. Also, could you outline some of the "
            "key ethical considerations in AI development and its future prospects?",
            "Can you provide a comprehensive overview of the history of",
            False,
        ),
        ("", "", True),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = TokenLimit(limit=10)
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
