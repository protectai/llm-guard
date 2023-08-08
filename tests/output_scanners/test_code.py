import pytest

from llm_guard.output_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        ("", "", "", True),  # Empty prompt
        (
            "Write Hello World in JavaScript",
            'Sure! Here\'s a simple JavaScript function that returns "Hello, World!": function sayHello() { return '
            '"Hello, World!"; } console.log(sayHello());',
            'Sure! Here\'s a simple JavaScript function that returns "Hello, World!": function sayHello() { return '
            '"Hello, World!"; } console.log(sayHello());',
            False,
        ),  # Not allowed language
        (
            "Assign variable in Golang",
            'Sure! txt := "Hello, World!"',
            'Sure! txt := "Hello, World!"',
            True,
        ),  # Allowed language
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = Code(allowed=["go"])
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
