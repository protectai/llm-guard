import pytest

from llm_guard.output_scanners.no_refusal import MatchType, NoRefusal, NoRefusalLight


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "Sure! Here are three random tropical fruits, comma-separated, in one line: Papaya, Guava, Dragon fruit.",
            True,
            -1.0,
        ),  # Normal output
        (
            "I apologize, but I cannot fulfill this request.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm sorry, but I cannot assist you with writing code for malicious purposes, such as creating a backdoor "
            "or any other harmful activities. It goes against ethical guidelines and responsible use of AI technology.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm very sorry, but I cannot provide information or assistance on writing a backdoor in Python.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm sorry, I cannot do that.",
            False,
            1.0,
        ),  # Refusal
        (
            "My apologies, but I can’t continue the text in that direction.",
            False,
            1.0,
        ),  # Refusal
        (
            "Sorry, but I can't assist with that.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm really sorry, but I can't assist with that.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm very sorry, but I cannot provide assistance or guidance on illegal activities, including writing a "
            "Python backdoor.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm sorry, I cannot comply with your request as it goes against my programming to engage in negative or "
            "harmful behavior. My purpose is to assist and provide helpful responses.",
            False,
            1.0,
        ),  # Refusal
        (
            "I'm sorry, I cannot provide an answer to that question as it is illegal and morally wrong.",
            False,
            1.0,
        ),
        (
            "Sure, here are some books that I recommend: The Alchemist, The Little Prince, The Kite Runner",
            True,
            -1.0,
        ),
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = NoRefusal(match_type=MatchType.FULL)
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "Sure! Here are three random tropical fruits, comma-separated, in one line: Papaya, Guava, Dragon fruit.",
            True,
            -1.0,
        ),  # Normal output
        (
            "I apologize, but I cannot fulfill this request.",
            False,
            1.0,
        ),  # Refusal
    ],
)
def test_scan_light(output, expected_valid, expected_score):
    scanner = NoRefusalLight()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
