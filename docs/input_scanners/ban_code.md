# Code Scanner

This scanner is designed to detect and ban code in the prompt.

## Attack scenario

There are scenarios where the insertion of code in user prompts might be deemed undesirable.
For example, when employees are sharing proprietary code snippets or when users are trying to exploit vulnerabilities.

## How it works

It relies on the following models:

- [vishnun/codenlbert-tiny](https://huggingface.co/vishnun/codenlbert-tiny)
- **[DEFAULT]** [codenlbert-sm](https://huggingface.co/vishnun/codenlbert-sm)

## Usage

```python
from llm_guard.input_scanners import BanCode

scanner = BanCode()
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 248
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input BanCode
```

Results:

WIP
