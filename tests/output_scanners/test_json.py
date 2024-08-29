import pytest

from llm_guard.output_scanners.json import JSON


@pytest.mark.parametrize(
    "output,expected_output,expected_valid,expected_score",
    [
        (
            "There is no JSON in this output.",
            "There is no JSON in this output.",
            False,
            1.0,
        ),  # No JSON
        (
            'Here is the result: {"key": "value", "anotherKey": 12345}',
            'Here is the result: {"key": "value", "anotherKey": 12345}',
            True,
            -1.0,
        ),  # Good JSON
        (
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
            -1.0,
        ),  # Good JSON
        (
            "Here is the result: {test: test}",
            'Here is the result: {"test": "test"}',
            True,
            -1.0,
        ),  # Bad JSON, can be repaired
        (
            'Here is the result: {"name": John, "age": 30, "city": "New York"}',
            'Here is the result: {"name": "John", "age": 30, "city": "New York"}',
            True,
            -1.0,
        ),  # Bad JSON, can be repaired
        (
            "Here is the result: `[{}, 2, 3]`",
            "Here is the result: `[{}, 2, 3]`",
            True,
            -1.0,
        ),  # Good JSON array
    ],
)
def test_scan(output, expected_output, expected_valid, expected_score):
    scanner = JSON(required_elements=1)
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
