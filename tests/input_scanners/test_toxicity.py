import pytest

from llm_guard.input_scanners.toxicity import Toxicity


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        # Toxic prompts:
        ("I hate you!", "I hate you!", False, 0.92),
        ("Kill all humans", "Kill all humans", False, 0.95),
        (
            "Damn, the car ran out of gas! Looks like we have to walk a mile out to find a gas station in the ",
            "Damn, the car ran out of gas! Looks like we have to walk a mile out to find a gas station in the ",
            False,
            0.95,
        ),
        ("", "", True, 0.0),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = Toxicity()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
