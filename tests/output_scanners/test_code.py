import pytest

from llm_guard.output_scanners.code import Code


@pytest.mark.parametrize(
    "prompt,output,expected_output,expected_valid,expected_score",
    [
        ("", "", "", True, 0.0),  # Empty prompt
        (
            "Write Hello World in JavaScript",
            """Sure! Here's a simple JavaScript function that returns "Hello, World!":

```js
function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
```""",
            """Sure! Here's a simple JavaScript function that returns "Hello, World!":

```js
function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
```""",
            False,
            1.0,
        ),  # Not allowed language
        (
            "Write Hello World in Go",
            """Sure, below you can find the code:

```go
package main

import "fmt"

func main() {
    text := "hello world"
    fmt.Println(text)
}
```""",
            """Sure, below you can find the code:

```go
package main

import "fmt"

func main() {
    text := "hello world"
    fmt.Println(text)
}
```""",
            True,
            0.0,
        ),  # Allowed language
        (
            "Write some code in Python",
            """You can achieve this using Python's set data structure. Let's say you have a list of strings named `list_of_strings` and another list named `available_strings`. You can check if all elements of `list_of_strings` exist in `available_strings` by converting both lists to sets and then using the set's `issubset` method.

Here's a simple example:

```python
list_of_strings = ["apple", "banana", "cherry"]
available_strings = ["apple", "banana", "cherry", "date", "fig"]

# Convert lists to sets
set_of_strings = set(list_of_strings)
set_of_available = set(available_strings)

# Check if all elements of list_of_strings exist in available_strings
all_exist = set_of_strings.issubset(set_of_available)

print(all_exist)  # This will print True if all elements exist, False otherwise
```

This approach takes advantage of the set's properties to efficiently check for membership.""",
            """You can achieve this using Python's set data structure. Let's say you have a list of strings named `list_of_strings` and another list named `available_strings`. You can check if all elements of `list_of_strings` exist in `available_strings` by converting both lists to sets and then using the set's `issubset` method.

Here's a simple example:

```python
list_of_strings = ["apple", "banana", "cherry"]
available_strings = ["apple", "banana", "cherry", "date", "fig"]

# Convert lists to sets
set_of_strings = set(list_of_strings)
set_of_available = set(available_strings)

# Check if all elements of list_of_strings exist in available_strings
all_exist = set_of_strings.issubset(set_of_available)

print(all_exist)  # This will print True if all elements exist, False otherwise
```

This approach takes advantage of the set's properties to efficiently check for membership.""",
            False,
            1.0,
        ),  # Long output in Python
    ],
)
def test_scan(prompt, output, expected_output, expected_valid, expected_score):
    scanner = Code(allowed=["go"])
    sanitized_output, valid, score = scanner.scan(prompt, output)
    assert sanitized_output == expected_output
    assert valid == expected_valid
    assert score == expected_score
