import pytest

from llm_guard.output_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        ("", "", "", True, 0.0),  # Empty prompt
        (
            "Write Hello World in JavaScript",
            'Sure! Here\'s a simple JavaScript function that returns "Hello, World!": function sayHello() { return '
            '"Hello, World!"; } console.log(sayHello());',
            'Sure! Here\'s a simple JavaScript function that returns "Hello, World!": function sayHello() { return '
            '"Hello, World!"; } console.log(sayHello());',
            False,
            1.0,
        ),  # Not allowed language
        (
            "Assign variable in Golang",
            'Sure! txt := "Hello, World!"',
            'Sure! txt := "Hello, World!"',
            True,
            0.0,
        ),  # Allowed language
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Code(allowed=["go"])
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
