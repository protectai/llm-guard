# Code Scanner

This scanner can be particularly useful in applications that need to accept only code snippets in specific languages.

## Attack scenario

In some contexts, having a language model inadvertently produce code in its output might be deemed undesirable or risky.
For instance, a user might exploit the model to generate malicious scripts or probe it for potential vulnerabilities.
Controlling and inspecting the code in the model's output can be paramount in ensuring user safety and system integrity.

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
from llm_guard.output_scanners import Code

scanner = Code(languages=["python"], is_blocked=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

### ONNX

The scanner can be optimized by using the ONNX converted model [laiyer/CodeBERTa-language-id-onnx](https://huggingface.co/laiyer/CodeBERTa-language-id-onnx). This can be done by setting the `use_onnx`.

Make sure to install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime] # for CPU instances
pip install llm-guard[onnxruntime-gpu] # for GPU instances
```

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 159
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output Code
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                    | 2.36             | 102.93                | 127.18                | 146.58                | 54.30                | 2928.04  |
| AWS m5.xlarge with ONNX          | 0.00             | 28.64                 | 28.94                 | 29.18                 | 27.82                | 5715.82  |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 6.47                  | 7.95                  | 9.14                  | 3.47                 | 45779.66 |
| Azure Standard_D4as_v4           | 3.72             | 126.67                | 157.04                | 181.34                | 65.39                | 2431.69  |
| Azure Standard_D4as_v4 with ONNX | 0.00             | 21.63                 | 21.81                 | 21.96                 | 19.86                | 8006.43  |
