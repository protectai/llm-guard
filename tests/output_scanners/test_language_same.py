import pytest

from llm_guard.output_scanners.language_same import LanguageSame


@pytest.mark.parametrize(
    "prompt,output,expected_valid,expected_score",
    [
        (
            "Describe me a random book",
            "This book is about testing, experimenting, and playing with language. It is a handbook of tools and techniques for taking words apart and putting them back together again in ways that I hope are meaningful and legitimate (or even illegitimate). This book is about peeling back layers in search of the language-making energy of the human spirit. It is about the gaps in meaning that we urgently need to notice and name—the places where our dreams and ideals are no longer fulfilled by a society that has become fast-paced and hyper-commercialized.",
            True,
            -1.0,
        ),  # Correct output
        (
            "What's your name? Write the answer in Spanish",
            "Me llamo Sofía",
            False,
            1.0,
        ),  # English prompt and Spanish output
    ],
)
def test_scan(prompt, output, expected_valid, expected_score):
    scanner = LanguageSame()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
