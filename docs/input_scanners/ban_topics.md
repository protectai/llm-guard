# Ban Topics Scanner

It is a proactive tool aimed at restricting specific topics, such as religion, from being introduced in the prompts.
This ensures that interactions remain within acceptable boundaries and avoids potentially sensitive or controversial
discussions.

## Attack

Certain topics, when used as prompts for Language Learning Models, can lead to outputs that might be deemed sensitive,
controversial, or inappropriate. By banning these topics, service providers can maintain the quality of interactions and
reduce the risk of generating responses that could lead to misunderstandings or misinterpretations.

## How it works

It relies on the capabilities of the
model: [MoritzLaurer/deberta-v3-base-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1).
This model aids in identifying the underlying theme or topic of a prompt, allowing the scanner to cross-check it against
a list of banned topics.

## Usage

```python
from llm_guard.input_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input BanTopics
```

Results:

| Instance          | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|-------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge     | 100          | 5          | 2.99             | 471.60                | 498.70                | 520.39                | 416.47               | 240.11 |
| AWS g5.xlarge GPU | 100          | 5          | 30.46            | 309.26                | 396.40                | 466.11                | 134.50               | 743.47 |
