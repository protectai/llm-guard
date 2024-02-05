# Code Scanner

This scanner is designed to detect and validate code in the prompt.

It can be particularly useful in applications that need to accept only code snippets in specific languages.

## Attack scenario

There are scenarios where the insertion of code in user prompts might be deemed undesirable. Users might be trying to
exploit vulnerabilities, test out scripts, or engage in other activities that are outside the platform's intended scope.
Monitoring and controlling the nature of the code can be crucial to maintain the integrity and safety of the system.

## How it works

Utilizing [philomath-1209/programming-language-identification](https://huggingface.co/philomath-1209/programming-language-identification) model, the scanner can identify code snippets within prompts across various programming languages.
Developers can configure the scanner to either allow or ban specific languages, thus retaining full control over which types of code can appear in user queries.

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

## Usage

```python
from llm_guard.input_scanners import Code

scanner = Code(languages=["Python"], is_blocked=True)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

[Read more](../usage/optimization.md)

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

WIP
