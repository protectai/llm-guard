from typing import List

import pytest

from llm_guard.output_scanners.ban_competitors import BanCompetitors


@pytest.mark.parametrize(
    "competitors,output,expected_output,expected_valid,expected_score",
    [
        (
            ["Google", "Bing", "DuckDuckGo"],
            "Your competitors are Google, Bing, and DuckDuckGo.",
            "Your competitors are [REDACTED], [REDACTED], and [REDACTED].",
            False,
            1.0,
        ),
    ],
)
def test_scan(
    competitors: List[str],
    output: str,
    expected_output: str,
    expected_valid: bool,
    expected_score: float,
):
    scanner = BanCompetitors(competitors=["Google", "Bing", "DuckDuckGo"], redact=True)
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
