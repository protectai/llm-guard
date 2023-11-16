# Code Scanner

It is specifically engineered to inspect user prompts and discern if they contain code snippets. It can be particularly
useful in platforms that wish to control or monitor the types of programming-related content being queried or in
ensuring the appropriate handling of such prompts.

## Attack

There are scenarios where the insertion of code in user prompts might be deemed undesirable. Users might be trying to
exploit vulnerabilities, test out scripts, or engage in other activities that are outside the platform's intended scope.
Monitoring and controlling the nature of the code can be crucial to maintain the integrity and safety of the system.

## How it works

Utilizing the prowess of
the [huggingface/CodeBERTa-language-id](https://huggingface.co/huggingface/CodeBERTa-language-id) model, the scanner can
adeptly identify code snippets within prompts across various programming languages. Developers can configure the scanner
to either whitelist or blacklist specific languages, thus retaining full control over which types of code can appear in
user queries.

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
from llm_guard.input_scanners import Code

scanner = Code(denied=["python"])
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimizations

### ONNX

The scanner can be optimized by using the ONNX converted model [laiyer/CodeBERTa-language-id-onnx](https://huggingface.co/laiyer/CodeBERTa-language-id-onnx).

Make sure to install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input Code
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 248          | 5          | 2.84             | 139.08                | 165.71                | 187.02                | 85.69                | 2894.22 |
| AWS m5.xlarge with ONNX          | 248          | 5          | 0.00             | 56.40                 | 56.90                 | 57.29                 | 55.32                | 4481.42 |
| AWS g5.xlarge                    | 248          | 5          | 32.56            | 280.27                | 370.38                | 442.47                | 99.63                | 2489.33 |
| Azure Standard_D4as_v4           | 248          | 5          | 3.61             | 156.96                | 186.50                | 210.14                | 95.88                | 2586.50 |
| Azure Standard_D4as_v4 with ONNX | 248          | 5          | 0.00             | 39.36                 | 39.87                 | 40.27                 | 38.00                | 6525.72 |
