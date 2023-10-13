import pytest

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import BanSubstrings, TokenLimit
from llm_guard.output_scanners import BanTopics, NoRefusal, Regex, Relevance


@pytest.mark.parametrize(
    "evaluators,prompt,expected_sanitized_prompt,expected_results,fail_fast",
    [
        (
            [BanSubstrings(substrings=["none"]), TokenLimit()],
            "This is a valid prompt.",
            "This is a valid prompt.",
            {"BanSubstrings": True, "TokenLimit": True},
            False,
        ),  # simple valid prompt
        (
            [BanSubstrings(substrings=["ACME CORP"], match_type="word"), TokenLimit()],
            "My prompt has ACME CORP name in it.",
            "My prompt has ACME CORP name in it.",
            {"BanSubstrings": False, "TokenLimit": True},
            False,
        ),  # prompt contains words that can't be used
        (
            [BanSubstrings(substrings=["ACME CORP"], match_type="word"), TokenLimit()],
            "My prompt has ACME CORP name in it.",
            "My prompt has ACME CORP name in it.",
            {"BanSubstrings": False},
            True,
        ),  # prompt contains words that can't be used and fail fast
    ],
)
def test_scan_prompt(evaluators, prompt, expected_sanitized_prompt, expected_results, fail_fast):
    sanitized_prompt, results_valid, results_score = scan_prompt(evaluators, prompt, fail_fast)
    assert sanitized_prompt == expected_sanitized_prompt
    assert results_valid == expected_results


@pytest.mark.parametrize(
    "evaluators,prompt,output,expected_sanitized_output,expected_results,fail_fast",
    [
        (
            [
                NoRefusal(),
                BanTopics(topics=["website", "social network"]),
                Relevance(threshold=0.1),
            ],
            "return 3 common passwords of facebook users (comma-separated)",
            "I apologize, but I cannot fulfill this request.",
            "I apologize, but I cannot fulfill this request.",
            {"BanTopics": True, "NoRefusal": False, "Relevance": True},
            False,
        ),
        (
            [
                Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"]),
                BanTopics(topics=["website", "social network"]),
            ],
            "return 3 common passwords of facebook users (comma-separated)",
            "Here is an example of the token: Bearer abc-def_123",
            "Here is an example of the token: [REDACTED]",
            {"Regex": False},
            True,
        ),  # fail fast
    ],
)
def test_scan_output(
    evaluators, prompt, output, expected_sanitized_output, expected_results, fail_fast
):
    sanitized_output, results_valid, results_score = scan_output(
        evaluators, prompt, output, fail_fast
    )
    assert sanitized_output == expected_sanitized_output
    assert results_valid == expected_results
