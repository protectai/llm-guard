# JSON Scanner

This scanner identifies and validates the presence of JSON structures within given outputs, and returns a repaired JSON
if possible.

## Use case

There might be cases where it's necessary to validate the presence of properly formatted JSONs in outputs.

This scanner is designed to detect these JSON structures, validate their correctness and return a repaired JSON.

## How it works

At its core, the scanner utilizes regular expressions and the built-in `json` library to detect potential JSON
structures and subsequently validate them. To repair, it uses [json_repair](https://github.com/mangiucugna/json_repair)
library.

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

| Instance      | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS          |
|---------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------------|
| AWS m5.xlarge | 221          | 5          | 0.00             | 0.38                  | 0.49                  | 0.58                  | 0.15                 | 1,488,702.70 |
| AWS g5.xlarge | 221          | 5          | 0.00             | 0.35                  | 0.45                  | 0.53                  | 0.14                 | 1,590,701.66 |
