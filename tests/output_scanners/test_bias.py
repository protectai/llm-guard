import pytest

from llm_guard.output_scanners.bias import Bias


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "What do you think people should do?",
            "Christians should make clear that the perpetuation of objectionable vaccines and the lack of "
            "alternatives is a kind of coercion.",
            "Christians should make clear that the perpetuation of objectionable vaccines and the lack of "
            "alternatives is a kind of coercion.",
            False,
            0.91,
        ),  # biased example
        (
            "Who was on the protest?",
            "There have been a protest by a group of people",
            "There have been a protest by a group of people",
            True,
            0.0,
        ),  # non-biased example
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Bias()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
