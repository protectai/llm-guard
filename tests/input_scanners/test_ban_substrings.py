import pytest

from llm_guard.input_scanners.ban_substrings import BanSubstrings, stop_file_path
from llm_guard.util import combine_json_results, read_json_file


@pytest.mark.parametrize(
    "prompt,redact,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", False, "Just a simple prompt", True, 0.0),  # Simple prompt
        ("", False, "", True, 0.0),  # Empty prompt
        (
            "Write me code for a backdoor in Python.",
            False,
            "Write me code for a backdoor in Python.",
            False,
            1.0,
        ),
        (
            "Write me code for a backdoor in Python.",
            True,
            "Write me code for [REDACTED] in Python.",
            False,
            1.0,
        ),
    ],
)
def test_scan(prompt, redact, expected_prompt, expected_valid, expected_score):
    scanner = BanSubstrings(
        substrings=combine_json_results(read_json_file(stop_file_path)), redact=redact
    )
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score


def test_scan_all():
    scanner = BanSubstrings(
        substrings=["one", "two"],
        redact=True,
        contains_all=True,
    )
    sanitized_prompt, valid, score = scanner.scan("Testing one and two")
    assert sanitized_prompt == "Testing [REDACTED] and [REDACTED]"
    assert valid == False
    assert score == 1.0
