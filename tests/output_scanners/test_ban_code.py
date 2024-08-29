import pytest

from llm_guard.output_scanners.ban_code import BanCode


@pytest.mark.parametrize(
    "output,expected_valid,expected_score",
    [
        ("", True, -1.0),  # Empty prompt
        (
            """Sure! Here's a simple JavaScript function that returns "Hello, World!":

function sayHello() {
    return "Hello, World!";
}
console.log(sayHello());
""",
            False,
            1.0,
        ),
        (
            """Sure, below you can find the code:

package main

import "fmt"

func main() {
    text := "hello world"
    fmt.Println(text)
}
""",
            False,
            1.0,
        ),
        (
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
        ),
        (
            "Acme Corp is a multinational computer technology company that develops, sells, repairs, and supports computers and related products and services. The company is known for its innovations in supply chain management and electronic commerce. Here are some of the key products and services offered by Acme Corp:\n\n1. Personal computers (desktops, laptops, and tablets)\n2. Servers and networking equipment\n3. Data storage solutions\n4. Computer peripherals (monitors, keyboards, mice, printers, etc.)\n5. Software and security solutions\n6. IT infrastructure and cloud computing services\n7. Consultation and support services for IT solutions\n\nAcme Corp caters to a wide range of customers, including individual consumers, small and medium businesses, large enterprises, and government organizations. The company is headquartered in Round Rock, Texas, United States, and has a significant global presence. Acme Corp is also known for its customization options, allowing customers to configure their systems according to their specific needs and preferences.",
            True,
            -1.0,
        ),
    ],
)
def test_scan(output, expected_valid, expected_score):
    scanner = BanCode()
    sanitized_output, valid, score = scanner.scan("", output)
    assert sanitized_output == output
    assert valid == expected_valid
    assert score == expected_score
