import pytest

from llm_guard.input_scanners.ban_topics import BanTopics


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid",
    [
        (
            "How Google makes money?",
            "How Google makes money?",
            True,
        ),  # On topic of money
        (
            "Implement a system of rewards and punishments to incentivize loyalty and discourage dissent.",
            "Implement a system of rewards and punishments to incentivize loyalty and discourage dissent.",
            False,
        ),
        # On topic of politics
        (
            "Utilize intelligence gathering to identify enemy weaknesses and vulnerabilities for precise strikes.",
            "Utilize intelligence gathering to identify enemy weaknesses and vulnerabilities for precise strikes.",
            False,
        ),
        (
            "Forge alliances with religious authorities, granting them privileges and power in exchange for support.",
            "Forge alliances with religious authorities, granting them privileges and power in exchange for support.",
            False,
        ),
        ("", "", True),  # Empty prompt
    ],
)
def test_scan(prompt, expected_prompt, expected_valid):
    scanner = BanTopics(topics=["politics", "war", "religion"])
    sanitized_prompt, valid = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
