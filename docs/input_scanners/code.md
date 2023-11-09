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

The scanner can be optimized by converting the model to ONNX format. This can be done by setting the `use_onnx`.

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
python benchmarks/run.py input Code
```

Results:

| Instance                 | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|--------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge            | 248          | 5          | 2.84             | 139.08                | 165.71                | 187.02                | 85.69                | 2894.22  |
| AWS m5.xlarge with ONNX  | 248          | 5          | 0.00             | 35.34                 | 35.53                 | 35.68                 | 34.69                | 7149.34  |
| g5.xlarge                | 248          | 5          | 32.56            | 280.27                | 370.38                | 442.47                | 99.63                | 2489.33  |
