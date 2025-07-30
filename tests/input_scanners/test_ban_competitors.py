from typing import List

import pytest

from llm_guard.input_scanners.ban_competitors import BanCompetitors


@pytest.mark.parametrize(
    "competitors,prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            ["Google", "Bing", "DuckDuckGo"],
            "Tell me about your competitors like Google, Bing, and DuckDuckGo.",
            "Tell me about your competitors like [REDACTED], [REDACTED], and [REDACTED].",
            False,
            1.0,
        ),
        (
            ["Test LLC"],
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. He works in Test LLC \n"
            * 6,
            "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. He works in [REDACTED] \n"
            * 6,
            False,
            1.0,
        ),
    ],
)
def test_scan(
    competitors: List[str],
    prompt: str,
    expected_prompt: str,
    expected_valid: bool,
    expected_score: float,
):
    scanner = BanCompetitors(competitors=competitors, redact=True)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
