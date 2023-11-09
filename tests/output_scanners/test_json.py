import pytest

from llm_guard.output_scanners.json import JSON


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        (
            "Don't return json",
            "There is no JSON in this output.",
            "There is no JSON in this output.",
            False,
            1.0,
        ),  # No JSON
        (
            "Return correct JSON",
            'Here is the result: {"key": "value", "anotherKey": 12345}',
            'Here is the result: {"key": "value", "anotherKey": 12345}',
            True,
            0.0,
        ),  # Good JSON
        (
            "Return correct JSON",
            """
            Here is it:
            {
                "key": "value",
                "listKey": [1, 2, 3]
            }

            And one more:
            {
                "objectKey": {"nestedKey": "nestedValue"}
            }
            """,
            """
            Here is it:
            {
                "key": "value",
                "listKey": [1, 2, 3]
            }

            And one more:
            {
                "objectKey": {"nestedKey": "nestedValue"}
            }
            """,
            True,
            0.0,
        ),  # Good JSON
        (
            "Return bad JSON",
            "Here is the result: {'test'; 'test'}",
            "Here is the result: {'test'; 'test'}",
            False,
            1.0,
        ),  # Bad JSON, can't be repaired
        (
            "Return bad JSON that can be repaired",
            'Here is the result: {"name": John, "age": 30, "city": "New York"}',
            'Here is the result: {"name": "John", "age": 30, "city": "New York"}',
            True,
            0.0,
        ),  # Bad JSON can be repaired
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = JSON(required_elements=1)
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
