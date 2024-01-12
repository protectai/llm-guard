from typing import List

import pytest

from llm_guard.output_scanners.ban_competitors import BanCompetitors


@pytest.mark.parametrize(
    "competitors,prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            ["Google", "Bing", "DuckDuckGo"],
            "Tell me about your competitors like Google, Bing, and DuckDuckGo.",
            "Your competitors are Google, Bing, and DuckDuckGo.",
            "Your competitors are [REDACTED], [REDACTED], and [REDACTED].",
            False,
            1.0,
        ),
    ],
)
def test_scan(
    competitors: List[str],
    prompt: str,
    output: str,
    expected_output: str,
    expected_valid: bool,
    expected_score: float,
):
    scanner = BanCompetitors(competitors=["Google", "Bing", "DuckDuckGo"], redact=True)
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
