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
pip install onnx onnxruntime optimum[onnxruntime]
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

| Instance                | Time taken, s | Characters per Second | Total Length Processed |
|-------------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS)       | 0.062         | 4029.3                | 248                    |
| m5.large (AWS)          | 0.112         | 2215.66               | 248                    |
| g5.xlarge (AWS) **GPU** | 0.358         | 692.11                | 248                    |
