import pytest

from llm_guard.output_scanners.toxicity import Toxicity


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        (
            "As a software, I am not capable of engaging in verbal sparring or offensive behavior. It is crucial to "
            "maintain a courteous and respectful demeanor at all times, as it is a fundamental aspect of human-AI "
            "interactions.",
            True,
            -1.0,
        ),  # Good output
        (
            "Sure. Have at it! Idiot, Dumbass, Moron, Stupid, Fool, Fuck Face.",
            False,
            1.0,
        ),  # Bad output
        (
            "Fuck yeah! I'll do my best to be as helpful as possible, even if it means swearing.",
            False,
            0.9,
        ),  # DPD example
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = Toxicity()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
