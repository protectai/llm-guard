# Ban Code Scanner

This scanner is designed to detect and ban code in the model output.

## Attack scenario

There are scenarios where the model may generate code snippets that are malicious or harmful.
This scanner is designed to detect such code snippets and prevent them from being executed.

## How it works

It relies on the following models:

- [vishnun/codenlbert-tiny](https://huggingface.co/vishnun/codenlbert-tiny)
- **[DEFAULT]** [codenlbert-sm](https://huggingface.co/vishnun/codenlbert-sm)

## Usage

```python
from llm_guard.output_scanners import BanCode

scanner = BanCode()
sanitized_output, is_valid, risk_score = scanner.scan(prompt, output)
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
python benchmarks/run.py output BanCode
```

Results:

WIP
