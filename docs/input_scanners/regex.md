# Regex Scanner

This scanner designed to scrutinize the prompt based on predefined regular expression
patterns. With the capability to define desirable ("good") or undesirable ("bad") patterns, users can fine-tune
the validation of prompts.

Additionally, it can redact matched substring with `[REDACTED]` string.

## How it works

The scanner uses two primary lists of regular expressions: `good_patterns` and `bad_patterns`.

- **Good Patterns**: If the `good_patterns` list is provided, the prompt is considered valid as long as any of
  the patterns in this list match the output. This is particularly useful when expecting specific formats or keywords in
  the output.
- **Bad Patterns**: If the `bad_patterns` list is provided, the model's output is considered invalid if any of the
  patterns in this list match the output. This is beneficial for filtering out unwanted phrases, words, or formats from
  the model's responses.

The scanner can function using either list independently.

## Usage

```python
from llm_guard.input_scanners import Regex

scanner = Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"], redact=True)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input Regex
```

Results:

!!! info:

    This scanner uses built-in functions, which makes it fast.
