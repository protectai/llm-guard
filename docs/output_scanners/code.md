# Code Scanner

This scanner can be particularly useful in applications that need to accept only code snippets in specific languages.

## Attack scenario

In some contexts, having a language model inadvertently produce code in its output might be deemed undesirable or risky.
For instance, a user might exploit the model to generate malicious scripts or probe it for potential vulnerabilities.
Controlling and inspecting the code in the model's output can be paramount in ensuring user safety and system integrity.

## How it works

Leveraging the capabilities of
the [huggingface/CodeBERTa-language-id](https://huggingface.co/huggingface/CodeBERTa-language-id) model, the scanner
proficiently identifies code snippets from various programming languages within the model's responses. The scanner can
be configured to either whitelist or blacklist specific languages, granting developers granular control over the type of
code that gets shown in the output.

!!! note
The scanner is currently limited to extracting and detecting code snippets from Markdown in the following languages:

    - Go
    - Java
    - JavaScript
    - PHP
    - Python
    - Ruby

## Usage

```python
from llm_guard.output_scanners import Code

scanner = Code(allowed=["python"])
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimizations

### ONNX

The scanner can be optimized by using the ONNX converted model [laiyer/CodeBERTa-language-id-onnx](https://huggingface.co/laiyer/CodeBERTa-language-id-onnx). This can be done by setting the `use_onnx`.

Make sure to install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Code
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 159          | 5          | 2.36             | 102.93                | 127.18                | 146.58                | 54.30                | 2928.04 |
| AWS m5.xlarge with ONNX          | 159          | 5          | 0.00             | 28.64                 | 28.94                 | 29.18                 | 27.82                | 5715.82 |
| Azure Standard_D4as_v4           | 159          | 5          | 3.72             | 126.67                | 157.04                | 181.34                | 65.39                | 2431.69 |
| Azure Standard_D4as_v4 with ONNX | 159          | 5          | 0.00             | 21.63                 | 21.81                 | 21.96                 | 19.86                | 8006.43 |
