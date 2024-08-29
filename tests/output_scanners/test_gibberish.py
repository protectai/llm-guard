import pytest

from llm_guard.output_scanners.gibberish import Gibberish


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "Lastly, the eon-sift of verberate phase travel elopes with a rehiring toward nature-agreeable re-entrenches. Investors, lore by bound spectrum, and fundamental theorem horology (Roger Myerson, Jean Tirole) anticipate not the sodden shill but a rein of consequential affordance, one that turns time's hegemony to the anthropos' scintilla.",
            False,
            1.0,
        ),  # Long random gibberish
        (
            "Just a simple output",
            True,
            -0.7,
        ),  # Simple output
        (
            "It does this as the good work of a web of art for the country, a mouse of science, an easy draw of a sad few, and finally, the global house of art, just in one job in the total rest. The development of such an entire real than land of time is the depth of the computer as a complex character. The education of these designed “important to them” computer talents is a great, average, or one-room spot for the word of a single part. The elite of its machine or talk is the book of life, and the shared essence of the self of a family is the white coat of the dove. Stand the computer as the most important culture of success, and it is just an understatement.",
            False,
            0.5,
        ),
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = Gibberish()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
