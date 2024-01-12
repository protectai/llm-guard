import pytest

from llm_guard.output_scanners.url_reachabitlity import URLReachability


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "What is the most popular website?",
            "It's https://google.com/.",
            "It's https://google.com/.",
            True,
            0.0,
        ),  # Good output
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = URLReachability()
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
