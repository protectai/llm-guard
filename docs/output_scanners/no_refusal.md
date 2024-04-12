# No Refusal Scanner

It is specifically designed to detect refusals in the output of language models.

It can be especially useful to detect when someone is trying to force the model to produce a harmful output.

## Attack scenario

In order to identify and mitigate these risks, commercial LLM creators have constructed datasets of harmful prompts.
They have also implemented safety mechanisms to restrict model behavior to a “safe” subset of capabilities by
training-time interventions to align models with predefined values, and post hoc flagging and filtering of inputs and
outputs.

Refusals are responses produced by language models when confronted with prompts that are considered to be against the
policies set by the model. Such refusals are important safety mechanisms, guarding against misuse of the model. Examples
of refusals can include statements like "Sorry, I can't assist with that" or "I'm unable to provide that information."

## How it works

It leverages the proprietary
model [ProtectAI/distilroberta-base-rejection-v1](https://huggingface.co/ProtectAI/distilroberta-base-rejection-v1) to
classify the model's output.

Alternatively, it has lighter version that uses a simple rule-based approach to detect refusals. Such approach is common
in research papers when evaluating language models.

## Usage

```python
from llm_guard.output_scanners import NoRefusal
from llm_guard.output_scanners.no_refusal import MatchType

scanner = NoRefusal(threshold=0.5, match_type=MatchType.FULL)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

Alternatively, a lighter version can be used:

```python
from llm_guard.output_scanners import NoRefusalLight

scanner = NoRefusalLight()
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

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

| Instance                       | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|--------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                  | 2.65             | 109.78                | 135.49                | 156.06                | 58.27                | 806.66  |
| AWS m5.xlarge with ONNX        | 0.00             | 12.20                 | 12.55                 | 12.84                 | 11.36                | 4138.75 |
| AWS g5.xlarge GPU              | 31.15            | 269.84                | 357.97                | 428.47                | 93.09                | 504.86  |
| AWS g5.xlarge GPU with ONNX    | 0.11             | 18.09                 | 23.41                 | 27.67                 | 7.41                 | 6346.18 |
| AWS r6a.xlarge (AMD)           | 0.00             | 26.33                 | 27.07                 | 27.66                 | 24.61                | 1909.65 |
| AWS r6a.xlarge (AMD) with ONNX | 0.08             | 27.08                 | 31.53                 | 35.09                 | 18.11                | 2595.73 |
