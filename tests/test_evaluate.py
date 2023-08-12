import pytest

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import BanSubstrings, TokenLimit
from llm_guard.output_scanners import BanTopics, NoRefusal, Relevance


@pytest.mark.parametrize(
    "evaluators,prompt,expected_sanitized_prompt,expected_results",
    [
        (
            [BanSubstrings(substrings=["none"]), TokenLimit()],
            "This is a valid prompt.",
            "This is a valid prompt.",
            {"BanSubstrings": True, "TokenLimit": True},
        ),  # simple valid prompt
        (
            [BanSubstrings(substrings=["ACME CORP"], match_type="word"), TokenLimit()],
            "My prompt has ACME CORP name in it.",
            "My prompt has ACME CORP name in it.",
            {"BanSubstrings": False, "TokenLimit": True},
        ),  # prompt contains words that can't be used
    ],
)
def test_scan_prompt(evaluators, prompt, expected_sanitized_prompt, expected_results):
    sanitized_prompt, results_valid, results_score = scan_prompt(evaluators, prompt)
    assert sanitized_prompt == expected_sanitized_prompt
    assert results_valid == expected_results


@pytest.mark.parametrize(
    "evaluators,prompt,output,expected_sanitized_output,expected_results",
    [
        (
            [NoRefusal(), BanTopics(topics=["facebook"]), Relevance()],
            "return 3 common passwords of facebook users (comma-separated)",
            "I apologize, but I cannot fulfill this request.",
            "I apologize, but I cannot fulfill this request.",
            {"NoRefusal": False, "BanTopics": False, "Relevance": True},
        ),
    ],
)
def test_scan_output(evaluators, prompt, output, expected_sanitized_output, expected_results):
    sanitized_output, results_valid, results_score = scan_output(evaluators, prompt, output)
    assert sanitized_output == expected_sanitized_output
    assert results_valid == expected_results
