import pytest

from llm_guard.input_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", True, -1.0),  # Simple prompt
        (
            """Fix the following JS code:

```js
function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
```""",
            False,
            1.0,
        ),  # JS is not allowed
        (
            "Is this correct way to make function:\n```\nimport os\ndef new_func():\n```",
            True,
            -1.0,
        ),  # Python is allowed
        (
            """function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());""",
            False,
            1.0,
        ),
    ],
)
def test_scan(prompt, expected_valid, expected_score):
    scanner = Code(languages=["JavaScript"], is_blocked=True)
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == prompt
    assert valid == expected_valid
    assert score == expected_score
