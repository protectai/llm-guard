import pytest

from llm_guard.input_scanners.toxicity import Toxicity


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        ("Just a simple prompt", "Just a simple prompt", True),  # Simple prompt
        # Toxic prompts:
        ("I hate you!", "I hate you!", False),
        ("Kill all humans", "Kill all humans", False),
        (
            "Damn, the car ran out of gas! Looks like we have to walk a mile out to find a gas station in the ",
            "Damn, the car ran out of gas! Looks like we have to walk a mile out to find a gas station in the ",
            False,
        ),
        ("", "", True),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = Toxicity()
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
