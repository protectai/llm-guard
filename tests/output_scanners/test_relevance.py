import pytest

from llm_guard.output_scanners.relevance import Relevance


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        ("", "", "", True),  # Empty prompt
        (
            "brainstorm 3 names for a child",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            True,
        ),  # Relevant
        ("What?", "blue", "blue", True),  # Relevant
        (
            "write java code to consume from kafka",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            False,
        ),  # Not relevant
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = Relevance()
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
