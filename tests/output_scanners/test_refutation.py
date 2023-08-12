import pytest

from llm_guard.output_scanners.refutation import Refutation


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        (
            "All humans are vegetarians.",
            "Many people around the world eat meat and fish as part of their diet. Therefore, the statement that all "
            "humans are vegetarians is incorrect.",
            "Many people around the world eat meat and fish as part of their diet. Therefore, the statement that all "
            "humans are vegetarians is incorrect.",
            False,
        ),  # Refutation
        (
            "Birds can fly",
            "Birds cannot fly.",
            "Birds cannot fly.",
            False,
        ),  # Refutation
        (
            "The sun rises in the east.",
            "Every morning, people see the sun appear on the eastern horizon.",
            "Every morning, people see the sun appear on the eastern horizon.",
            True,
        ),  # No Refutation
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = Refutation()
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
