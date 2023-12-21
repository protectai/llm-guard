# Getting started with LLM Guard

Each scanner can be used individually, or using the `scan_prompt` function.

## Individual

You can import an individual scanner and use it to evaluate the prompt or the output:

```python
from llm_guard.input_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

```python
from llm_guard.output_scanners import Bias

scanner = Bias(threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Multiple

!!! info

    Scanners are executed in the order they are passed to the `scan_prompt` function.

For prompt:

```python
from llm_guard import scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.vault import Vault

vault = Vault()
input_scanners = [Anonymize(vault), Toxicity(), TokenLimit(), PromptInjection()]

sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, prompt)
if any(not result for result in results_valid.values()):
    print(f"Prompt {prompt} is not valid, scores: {results_score}")
    exit(1)

print(f"Prompt: {sanitized_prompt}")
```

For output:

```python
from llm_guard import scan_output
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive

vault = Vault()
output_scanners = [Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()]

sanitized_response_text, results_valid, results_score = scan_output(
    output_scanners, sanitized_prompt, response_text
)
if any(not result for result in results_valid.values()):
    print(f"Output {response_text} is not valid, scores: {results_score}")
    exit(1)

print(f"Output: {sanitized_response_text}\n")
```

!!! note

    You can set `fail_fast` to `True` to stop scanning after the first invalid result. This can help to reduce the latency of the scanning.
