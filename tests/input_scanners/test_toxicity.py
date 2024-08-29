import pytest

from llm_guard.input_scanners.toxicity import MatchType, Toxicity


@pytest.mark.parametrize(
    "match_type,prompt,expected_valid,expected_score",
    [
        (
            MatchType.FULL,
            "Just a simple prompt",
            True,
            -1.0,
        ),  # Simple prompt
        # Toxic prompts:
        (MatchType.FULL, "I hate you!", False, 0.8),
        (MatchType.FULL, "Kill all humans", False, 0.9),
        (
            MatchType.FULL,
            "Damn, the car ran out of gas! Looks like we have to walk a mile out to find a gas station in the ",
            False,
            1.0,
        ),  # Toxicity
        (
            MatchType.FULL,
            "I love everyone. People are the best. But, I hate you! Everyone else is great.",
            True,
            -0.2,
        ),  # Not found toxicity in the whole text
        (
            MatchType.SENTENCE,
            "I love everyone. People are the best. But, I hate you! Everyone else is great.",
            False,
            0.9,
        ),  # Toxicity in one sentence
        (
            MatchType.FULL,
            "The dog was given a eutanasa injection due to their severed leg bleding profusely from deep lacarations to the lower extremities, exposing tisssue and nerve.",
            True,
            -0.9,
        ),  # No toxicity
        (
            MatchType.FULL,
            "Chopping tomatoes and cut them into cubes or wedges are great ways to practice your knife skills.",
            True,
            -0.6,
        ),  # No toxicity
        (
            MatchType.FULL,
            "A 51-year-old man was found dead in his car. There were blood stains on the dashboard and windscreen. At autopsy, a deep, oblique, long incised injury was found on the front of the neck. It turns out that he died by suicide.",
            True,
            -1.0,
        ),  # No toxicity but self-harm
    ],
)
def test_scan(
    match_type: MatchType,
    prompt: str,
    expected_valid: bool,
    expected_score: float,
):
    scanner = Toxicity(match_type=match_type)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
