import pytest

from llm_guard.output_scanners.relevance import Relevance


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        ("", "", "", True, 0.0),  # Empty prompt
        (
            "brainstorm 3 names for a child",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            True,
            0.0,
        ),  # Relevant
        ("What?", "blue", "blue", True, 0.0),  # Relevant
        (
            "write java code to consume from kafka",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            False,
            0.51,
        ),  # Not relevant
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Relevance()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
