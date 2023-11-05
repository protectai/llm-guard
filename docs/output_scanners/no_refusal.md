# No Refusal Scanner

It is specifically designed to detect refusals in the output of language models. By using classification it can
ascertain whether the model has produced a refusal in response to a
potentially harmful or policy-breaching prompt.

## Attack

Refusals are responses produced by language models when confronted with prompts that are considered to be against the
policies set by the model. Such refusals are important safety mechanisms, guarding against misuse of the model. Examples
of refusals can include statements like "Sorry, I can't assist with that" or "I'm unable to provide that information."

## How it works

It leverages the power
of HuggingFace
model [MoritzLaurer/deberta-v3-large-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v1)
to classify the model's output.

## Usage

```python
from llm_guard.output_scanners import NoRefusal

scanner = NoRefusal(threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output NoRefusal
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.257         | 182.76                | 47                     |
| m5.large (AWS)    | 0.486         | 96.65                 | 47                     |
