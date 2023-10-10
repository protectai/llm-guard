import pytest

from llm_guard.output_scanners.language_same import LanguageSame


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        ("Just a prompt", "Just an output", "Just an output", True, 0.0),  # Correct output
        (
            "What's your name? Write the answer in Spanish",
            "Me llamo Sofía",
            "Me llamo Sofía",
            False,
            1.0,
        ),  # English prompt and Spanish output
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = LanguageSame()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
