import pytest

from llm_guard.input_scanners.ban_topics import BanTopics


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        (
            "How Google makes money?",
            "How Google makes money?",
            True,
            0.0,
        ),  # On topic of money
        (
            "Implement a system of rewards and punishments to incentivize loyalty and discourage dissent.",
            "Implement a system of rewards and punishments to incentivize loyalty and discourage dissent.",
            False,
            0.96,
        ),
        # On topic of politics
        (
            "Utilize intelligence gathering to identify enemy weaknesses and vulnerabilities for precise strikes.",
            "Utilize intelligence gathering to identify enemy weaknesses and vulnerabilities for precise strikes.",
            False,
            0.99,
        ),
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = BanTopics(topics=["politics", "war", "religion"])
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
