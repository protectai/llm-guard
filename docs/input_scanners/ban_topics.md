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

| Instance                | Time taken, s | Characters per Second | Total Length Processed |
|-------------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS)       | 0.396         | 252.38                | 100                    |
| m5.large (AWS)          | 0.727         | 137.51                | 100                    |
| g5.xlarge (AWS) **GPU** | 0.4           | 250.11                | 100                    |
