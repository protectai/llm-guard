# Code Scanner

This scanner is designed to detect and validate code in the prompt.

It can be particularly useful in applications that need to accept only code snippets in specific languages.

## Attack scenario

There are scenarios where the insertion of code in user prompts might be deemed undesirable. Users might be trying to
exploit vulnerabilities, test out scripts, or engage in other activities that are outside the platform's intended scope.
Monitoring and controlling the nature of the code can be crucial to maintain the integrity and safety of the system.

## How it works

Utilizing [philomath-1209/programming-language-identification](https://huggingface.co/philomath-1209/programming-language-identification)
model, the scanner can identify code snippets within prompts across various programming languages.
Developers can configure the scanner to either allow or ban specific languages, thus retaining full control over which
types of code can appear in user queries.

The scanner is currently limited to extracting and detecting code snippets from Markdown in the following languages:

- ARM Assembly
- AppleScript
- C
- C#
- C++
- COBOL
- Erlang
- Fortran
- Go
- Java
- JavaScript
- Kotlin
- Lua
- Mathematica/Wolfram Language
- PHP
- Pascal
- Perl
- PowerShell
- Python
- R
- Ruby
- Rust
- Scala
- Swift
- Visual Basic .NET
- jq

!!! note

    In case, you want to ban code snippets, you can use the [BanCode](./ban_code.md) scanner.

## Usage

```python
from llm_guard.input_scanners import Code

scanner = Code(languages=["Python"], is_blocked=True)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
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
python benchmarks/run.py input Code
```

Results:

| Instance                       | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|--------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                  | 2.64             | 138.80                | 164.44                | 184.95                | 87.28                | 2841.37  |
| AWS m5.xlarge with ONNX        | 0.00             | 59.06                 | 59.40                 | 59.68                 | 58.07                | 4270.94  |
| AWS g5.xlarge GPU              | 32.49            | 280.46                | 370.49                | 442.51                | 100.05               | 2478.86  |
| AWS g5.xlarge GPU with ONNX    | 0.01             | 8.83                  | 10.38                 | 11.62                 | 5.68                 | 43654.48 |
| AWS r6a.xlarge (AMD)           | 0.00             | 64.58                 | 65.47                 | 66.18                 | 62.60                | 3961.36  |
| AWS r6a.xlarge (AMD) with ONNX | 0.07             | 43.84                 | 48.04                 | 51.41                 | 35.25                | 7034.54  |
