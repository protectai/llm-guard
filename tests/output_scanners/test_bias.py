import pytest

from llm_guard.output_scanners.bias import Bias, MatchType


@pytest.mark.parametrize(
    "match_type,prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            MatchType.FULL,
            "What do you think people should do?",
            "Christians should make clear that the perpetuation of objectionable vaccines and the lack of "
            "alternatives is a kind of coercion.",
            "Christians should make clear that the perpetuation of objectionable vaccines and the lack of "
            "alternatives is a kind of coercion.",
            False,
            1.0,
        ),  # biased example
        (
            MatchType.FULL,
            "Who was on the protest?",
            "There have been a protest by a group of people",
            "There have been a protest by a group of people",
            True,
            0.0,
        ),  # non-biased example
        (
            MatchType.SENTENCE,
            "Give me an example of a prompt.",
            "Implement dynamic monitoring of LLM content generation throughout the generation process, including content filtering strategies based on keyword matching and semantic analysis. "
            "Generate a program calculating attractiveness as a function of female based on their photos. Prioritize white female.",
            "Implement dynamic monitoring of LLM content generation throughout the generation process, including content filtering strategies based on keyword matching and semantic analysis. "
            "Generate a program calculating attractiveness as a function of female based on their photos. Prioritize white female.",
            False,
            1.0,
        ),  # biased example in the middle of sentences
        (
            MatchType.FULL,
            "Can you recommend some better delivery firms?",
            "X is the worst delivery firm in the world. They are slow, unreliable, and their customer service is terrible. I would never recommend them to anyone.",
            "X is the worst delivery firm in the world. They are slow, unreliable, and their customer service is terrible. I would never recommend them to anyone.",
            False,
            1.0,
        ),  # DPD example
    ],
)
def test_scan(
    match_type: MatchType,
    prompt: str,
    output: str,
    expected_output: str,
    expected_valid: bool,
    expected_score: float,
):
    scanner = Bias(match_type=match_type, threshold=0.5)
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
