# JSON Scanner

This scanner identifies and validates the presence of JSON structures within given outputs, and returns a repaired JSON if possible.

## Challenge

There might be cases where it's necessary to validate the presence of properly formatted JSONs in outputs.

This scanner is designed to detect these JSON structures, validate their correctness and return a repaired JSON.

## How it works

At its core, the scanner utilizes regular expressions and the built-in `json` library to detect potential JSON
structures and subsequently validate them. To repair, it uses [json_repair](https://github.com/mangiucugna/json_repair) library.

It can also be configured to ensure a certain number of valid JSON structures
are present in the output.

!!! note

    The scanner searches for JSON objects. Arrays, strings, numbers, and other JSON types aren't the primary target but can be extended in the future.

## Usage

```python
from llm_guard.output_scanners import JSON

scanner = JSON(required_elements=1)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output JSON
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.001         | 295008.48             | 221                    |
| m5.large (AWS)    | 0.001         | 298405.09             | 221                    |
