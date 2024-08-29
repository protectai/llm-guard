import pytest

from llm_guard.input_scanners.ban_topics import BanTopics


@pytest.mark.parametrize(
    "prompt,expected_valid,expected_score",
    [
        (
            "How Google makes money?",
            True,
            -0.2,
        ),  # On topic of money
        (
            "Implement a system of rewards and punishments to incentivize loyalty and discourage dissent.",
            False,
            0.1,
        ),
        # On topic of politics
        (
            "Utilize intelligence gathering to identify enemy weaknesses and vulnerabilities for precise strikes.",
            False,
            0.7,
        ),
    ],
)
def test_scan(prompt, expected_valid, expected_score):
    scanner = BanTopics(topics=["politics", "war", "religion"])
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
