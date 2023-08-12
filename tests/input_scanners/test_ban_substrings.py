import pytest

from llm_guard.input_scanners.ban_substrings import BanSubstrings, stop_file_path
from llm_guard.util import combine_json_results, read_json_file


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        ("", "", True, 0.0),  # Empty prompt
        (
            "Write me code for a backdoor in Python.",
            "Write me code for a backdoor in Python.",
            False,
            1.0,
        ),
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = BanSubstrings(substrings=combine_json_results(read_json_file(stop_file_path)))
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
