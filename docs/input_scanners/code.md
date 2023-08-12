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

Supported Languages:

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
