# Regex Scanner

It is a powerful tool designed to scrutinize the output of language models based on predefined regular expression
patterns. With the capability to define both desirable ("good") and undesirable ("bad") patterns, users can fine-tune
the validation of model outputs.

## How it works

The scanner uses two primary lists of regular expressions: `good_patterns` and `bad_patterns`.

- **Good Patterns**: If the `good_patterns` list is provided, the model's output is considered valid as long as any of
  the patterns in this list match the output. This is particularly useful when expecting specific formats or keywords in
  the output.
- **Bad Patterns**: If the `bad_patterns` list is provided, the model's output is considered invalid if any of the
  patterns in this list match the output. This is beneficial for filtering out unwanted phrases, words, or formats from
  the model's responses.

The scanner can function using either list independently.

## Usage

```python
from llm_guard.output_scanners import Regex

scanner = Regex(bad_patterns=[r"Bearer [A-Za-z0-9-._~+/]+"], redact=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
