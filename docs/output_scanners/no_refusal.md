# No Refusal Scanner

It is specifically designed to detect refusals in the output of language models.

It can be especially useful to detect when someone is trying to force the model to produce a harmful output.

## Attack scenario

In order to identify and mitigate these risks, commercial LLM creators have constructed datasets of harmful prompts.
They have also implemented safety mechanisms to restrict model behavior to a “safe” subset of capabilities by
training-time interventions to align models with predefined values, and post hoc flagging and filtering of inputs and outputs.

Refusals are responses produced by language models when confronted with prompts that are considered to be against the
policies set by the model. Such refusals are important safety mechanisms, guarding against misuse of the model. Examples
of refusals can include statements like "Sorry, I can't assist with that" or "I'm unable to provide that information."

## How it works

It leverages the proprietary model [laiyer/distilroberta-base-rejection-v1](https://huggingface.co/laiyer/distilroberta-base-rejection-v1) to classify the model's output.

## Usage

```python
from llm_guard.output_scanners import NoRefusal
from llm_guard.output_scanners.no_refusal import MatchType

scanner = NoRefusal(threshold=0.5, match_type=MatchType.FULL)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

[Read more](../usage/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 47
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output NoRefusal
```

Results:

WIP
