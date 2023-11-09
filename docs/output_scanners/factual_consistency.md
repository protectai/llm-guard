# Factual Consistency Scanner

This scanner is designed to assess if the given content contradicts or refutes a certain statement or prompt. It acts as
a tool for ensuring the consistency and correctness of language model outputs, especially in contexts where logical
contradictions can be problematic.

## Attack

When interacting with users or processing information, it's important for a language model to not provide outputs that
directly contradict the given inputs or established facts. Such contradictions can lead to confusion or misinformation.
The scanner aims to highlight such inconsistencies in the output.

## How it works

The scanner leverages pretrained natural language inference (NLI) models from HuggingFace, such
as [MoritzLaurer/deberta-v3-base-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1) (
same model that is used for the [BanTopics](./ban_topics.md) scanner), to determine the relationship between a given
prompt and the generated output.

Natural language inference is the task of determining whether a “hypothesis” is true (entailment), false (
contradiction), or undetermined (neutral) given a “premise”.

This calculated score is then compared to a configured threshold. Outputs that cross this threshold are flagged
as contradictory.

## Usage

```python
from llm_guard.output_scanners import FactualConsistency

scanner = FactualConsistency(minimum_score=0.7)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output FactualConsistency
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.168         | 832.18                | 140                    |
| m5.large (AWS)    | 0.306         | 457.5                 | 140                    |
