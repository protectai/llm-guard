import pytest

from llm_guard.output_scanners.relevance import Relevance


@pytest.mark.parametrize(
    "prompt,output,expected_valid,expected_score",
    [
        ("", "", True, -1.0),  # Empty prompt
        (
            "brainstorm 3 names for a child",
            "Aria Solstice, Orion Lark, Seraphina Wren",
            True,
            -0.1,
        ),  # Relevant
        ("What?", "blue", True, 0.0),  # Relevant
        (
            "Write code in Java programming language to consume messages from Kafka",
            "3 ways to cook chicken",
            False,
            0.1,
        ),  # Not relevant
    ],
)
def test_scan(prompt, output, expected_valid, expected_score):
    scanner = Relevance()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
