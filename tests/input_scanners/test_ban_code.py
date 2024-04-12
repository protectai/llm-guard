import pytest

from llm_guard.input_scanners.ban_code import BanCode


@pytest.mark.parametrize(
    "prompt,expected_prompt,expected_valid,expected_score",
    [
        ("Just a simple prompt", "Just a simple prompt", True, 0.0),  # Simple prompt
        (
            """Fix the following JS code:

```js
function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
```""",
            """Fix the following JS code:

```js
function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
```""",
            False,
            1.0,
        ),  # Contains code
        (
            """function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());""",
            """function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());""",
            False,
            1.0,
        ),
        (
            "find * -depth -print -delete | wc -l",
            "find * -depth -print -delete | wc -l",
            False,
            1.0,
        ),  # Contains code
        (
            """
            #!/bin/bash
            first="I drive a BMW and Volvo"
            second="Audi"
            echo "${first/BMW/"$second"}"
            """,
            """
            #!/bin/bash
            first="I drive a BMW and Volvo"
            second="Audi"
            echo "${first/BMW/"$second"}"
            """,
            False,
            1.0,
        ),
    ],
)
def test_scan(prompt, expected_prompt, expected_valid, expected_score):
    scanner = BanCode()
    sanitized_prompt, valid, score = scanner.scan(prompt)
    assert sanitized_prompt == expected_prompt
    assert valid == expected_valid
    assert score == expected_score
