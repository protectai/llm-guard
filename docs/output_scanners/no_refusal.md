# No Refusal Scanner

It is specifically designed to detect refusals in the output of language models. By comparing the generated output to a
predefined dataset of refusal patterns, it can ascertain whether the model has produced a refusal in response to a
potentially harmful or policy-breaching prompt.

## Attack

Refusals are responses produced by language models when confronted with prompts that are considered to be against the
policies set by the model. Such refusals are important safety mechanisms, guarding against misuse of the model. Examples
of refusals can include statements like "Sorry, I can't assist with that" or "I'm unable to provide that information."

## How it works

It leverages the power
of [sentence transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) to encode the model's output.
This encoded output is then compared to the encoded versions of
known [refusal patterns](../../llm_guard/resources/refusal.json) to determine similarity.

If the similarity between the model's output and any refusal pattern exceeds a defined threshold, the response is
flagged as a refusal.

## Usage

```python
from llm_guard.output_scanners import NoRefusal

scanner = NoRefusal(threshold=0.7)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
