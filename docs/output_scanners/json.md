# JSON Scanner

This scanner identifies and validates the presence of JSON structures within given outputs.

## Challenge

There might be cases where it's necessary to validate the presence of properly formatted JSONs in outputs.

This scanner is designed to detect these JSON structures and validate their correctness.

## How it works

At its core, the scanner utilizes regular expressions and the built-in `json` library to detect potential JSON structures and subsequently validate them. It can also be configured to ensure a certain number of valid JSON structures are present in the output.

!!! note

    The scanner searches for JSON objects. Arrays, strings, numbers, and other JSON types aren't the primary target but can be extended in the future.

## Usage

```python
from llm_guard.output_scanners import JSON

scanner = JSON(required_elements=1)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
