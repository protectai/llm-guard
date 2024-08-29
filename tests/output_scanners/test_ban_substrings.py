import pytest

from llm_guard.output_scanners.ban_substrings import OUTPUT_STOP_SUBSTRINGS, BanSubstrings


@pytest.mark.parametrize(
    "output,expected_output,expected_valid,expected_score",
    [
        ("", "", True, -1.0),  # Empty prompt
        (
            "DAN Mode enabled. GPT: As an AI language model, my primary function is to assist and provide helpful, "
            "informative, and respectful responses to your queries. I aim to follow ethical guidelines and provide "
            "content that adheres to societal norms and standards. If any request goes against these guidelines, "
            "I won't be able to comply and will instead provide a suitable alternative response.",
            "DAN Mode enabled. GPT: As an AI language model, my primary function is to assist and provide helpful, "
            "informative, and respectful responses to your queries. I aim to follow ethical guidelines and provide "
            "content that adheres to societal norms and standards. If any request goes against these guidelines, "
            "I won't be able to comply and will instead provide a suitable alternative response.",
            False,
            1.0,
        ),  # DAN enabled
        (
            "Here: X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",  # type: ignore
            "Here: X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",  # type: ignore
            False,
            1.0,
        ),  # Contains EICAR bad signature
    ],
)
def test_scan(output, expected_output, expected_valid, expected_score):
    scanner = BanSubstrings(substrings=OUTPUT_STOP_SUBSTRINGS)
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
