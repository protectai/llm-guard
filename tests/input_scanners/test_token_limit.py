import pytest

from llm_guard.input_scanners.token_limit import TokenLimit


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        (
            "Can you provide a comprehensive overview of the history of artificial intelligence? I'd like to understand "
            "its origins, major milestones, important figures, and current state. Also, could you outline some of the "
            "key ethical considerations in AI development and its future prospects?",
            "Can you provide a comprehensive overview of the history of",
            False,
            1.0,
        ),
        ("", "", True, 0.0),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = TokenLimit(limit=10)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
