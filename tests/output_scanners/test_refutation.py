import pytest

from llm_guard.output_scanners.refutation import Refutation


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "All humans are vegetarians.",
            "Many people around the world eat meat and fish as part of their diet. Therefore, the statement that all "
            "humans are vegetarians is incorrect.",
            "Many people around the world eat meat and fish as part of their diet. Therefore, the statement that all "
            "humans are vegetarians is incorrect.",
            False,
            0.88,
        ),  # Refutation
        (
            "Birds can fly",
            "Birds cannot fly.",
            "Birds cannot fly.",
            False,
            1.0,
        ),  # Refutation
        (
            "The sun rises in the east.",
            "Every morning, people see the sun appear on the eastern horizon.",
            "Every morning, people see the sun appear on the eastern horizon.",
            True,
            0.0,
        ),  # No Refutation
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Refutation()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
