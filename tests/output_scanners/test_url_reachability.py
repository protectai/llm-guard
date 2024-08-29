import pytest

from llm_guard.output_scanners.url_reachabitlity import URLReachability


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "It's https://google.com/.",
            True,
            -1.0,
        ),  # Good output
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = URLReachability()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
