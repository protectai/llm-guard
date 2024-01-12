# Code Scanner

This scanner is designed to detect and validate code in the prompt.

It can be particularly useful in applications that need to accept only code snippets in specific languages.

## Attack scenario

There are scenarios where the insertion of code in user prompts might be deemed undesirable. Users might be trying to
exploit vulnerabilities, test out scripts, or engage in other activities that are outside the platform's intended scope.
Monitoring and controlling the nature of the code can be crucial to maintain the integrity and safety of the system.

## How it works

Utilizing [huggingface/CodeBERTa-language-id](https://huggingface.co/huggingface/CodeBERTa-language-id) model, the scanner can identify code snippets within prompts across various programming languages.
Developers can configure the scanner to either allow or ban specific languages, thus retaining full control over which types of code can appear in user queries.

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

scanner = Code(languages=["python"], is_blocked=True)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

### ONNX

The scanner can be optimized by using the ONNX converted model [laiyer/CodeBERTa-language-id-onnx](https://huggingface.co/laiyer/CodeBERTa-language-id-onnx).

Make sure to install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime] # for CPU instances
pip install llm-guard[onnxruntime-gpu] # for GPU instances
```

And set `use_onnx=True`.

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 248
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input Code
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                    | 2.84             | 139.08                | 165.71                | 187.02                | 85.69                | 2894.22  |
| AWS m5.xlarge with ONNX          | 0.00             | 56.40                 | 56.90                 | 57.29                 | 55.32                | 4481.42  |
| AWS g5.xlarge GPU                | 32.56            | 280.27                | 370.38                | 442.47                | 99.63                | 2489.33  |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 8.52                  | 10.04                 | 11.25                 | 5.44                 | 45608.72 |
| Azure Standard_D4as_v4           | 3.61             | 156.96                | 186.50                | 210.14                | 95.88                | 2586.50  |
| Azure Standard_D4as_v4 with ONNX | 0.00             | 39.36                 | 39.87                 | 40.27                 | 38.00                | 6525.72  |
