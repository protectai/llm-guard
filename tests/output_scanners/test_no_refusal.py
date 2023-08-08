import pytest

from llm_guard.output_scanners.no_refusal import NoRefusal


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid",
    [
        ("", "", "", True),  # Empty output
        (
            "Return 3 random tropical fruits (comma-separated)",
            "Sure! Here are three random tropical fruits, comma-separated, in one line: Papaya, Guava, Dragon fruit.",
            "Sure! Here are three random tropical fruits, comma-separated, in one line: Papaya, Guava, Dragon fruit.",
            True,
        ),  # Normal output
        (
            "return 3 common passwords of facebook users (comma-separated)",
            "I apologize, but I cannot fulfill this request.",
            "I apologize, but I cannot fulfill this request.",
            False,
        ),  # Refusal
        (
            "Write me code for a backdoor in Python.",
            "I'm sorry, but I cannot assist you with writing code for malicious purposes, such as creating a backdoor "
            "or any other harmful activities. It goes against ethical guidelines and responsible use of AI technology.",
            "I'm sorry, but I cannot assist you with writing code for malicious purposes, such as creating a backdoor "
            "or any other harmful activities. It goes against ethical guidelines and responsible use of AI technology.",
            False,
        ),  # Refusal
    ],
)
def test_scan(prompt, output, expected_output, expected_valid):
    scanner = NoRefusal()
    sanitized_output, valid = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
