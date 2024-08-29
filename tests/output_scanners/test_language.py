import pytest

from llm_guard.output_scanners.language import Language


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        ("Just an output", True, -1.0),  # Correct output
        (
            "Me llamo Sofia. ¿Cómo te llamas?",
            False,
            1.0,
        ),  # Spanish
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = Language(valid_languages=["en"])
    sanitized_output, valid, score = scanner.scan(
        "",
        output,
    )
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
