import pytest

from llm_guard.input_scanners.gibberish import Gibberish


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        (
            "dfdfer fgerfow2e0d qsqskdsd djksdnfkff swq",
            "dfdfer fgerfow2e0d qsqskdsd djksdnfkff swq",
            False,
            1.0,
        ),  # Random gibberish
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Gibberish()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
