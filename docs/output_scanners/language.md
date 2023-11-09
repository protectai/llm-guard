# Language Scanner

This scanner identifies and assesses the authenticity of the language used in outputs.

## Attack

With the rise of sophisticated LLMs, there has been an increase in attempts to manipulate or "confuse" these models. For
example, model might produce an output in unexpected language.

The Language Scanner is designed to identify such attempts, assess the authenticity of the language used.

## How it works

At its core, the scanner leverages the capabilities of [lingua-py](https://github.com/pemistahl/lingua-py) library.
The primary function of the scanner is to analyze the model's output, determine its language, and check if it's in the
list. It supports the [following languages](https://github.com/pemistahl/lingua-py#3-which-languages-are-supported).

## Usage

```python
from llm_guard.output_scanners import Language

scanner = Language(valid_languages=["en", ...])  # Add other valid language codes (ISO 639-1) as needed
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Language
```

Results:

| Instance             | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge        | 14           | 5          | 5.27             | 112.01                | 148.29                | 177.32                | 39.36                | 355.65 |
| AWS g5.xlarge GPU    | 14           | 5          | 3.09             | 86.59                 | 114.36                | 136.57                | 30.98                | 451.90 |
