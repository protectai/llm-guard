# Factual Consistency Scanner

This scanner is designed to assess if the given content contradicts or refutes a certain statement or prompt. It acts as
a tool for ensuring the consistency and correctness of language model outputs, especially in contexts where logical
contradictions can be problematic.

## Attack scenario

When interacting with users or processing information, it's important for a language model to not provide outputs that
directly contradict the given inputs or established facts. Such contradictions can lead to confusion or misinformation.
The scanner aims to highlight such inconsistencies in the output.

## How it works

The scanner leverages pretrained natural language inference (NLI) models from HuggingFace, such
as [MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33) (
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

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 140
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output FactualConsistency
```

Results:

| Instance                       | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|--------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                  | 3.01             | 234.94                | 262.31                | 284.20                | 180.00               | 777.78   |
| AWS m5.xlarge with ONNX        | 0.09             | 98.62                 | 103.28                | 107.01                | 89.00                | 1573.02  |
| AWS g5.xlarge GPU              | 34.23            | 295.96                | 388.34                | 462.24                | 110.70               | 1264.69  |
| AWS g5.xlarge GPU with ONNX    | 0.01             | 11.18                 | 13.02                 | 14.49                 | 7.42                 | 18879.18 |
| AWS r6a.xlarge (AMD)           | 0.01             | 158.44                | 159.58                | 160.48                | 155.72               | 899.07   |
| AWS r6a.xlarge (AMD) with ONNX | 0.07             | 91.28                 | 95.30                 | 98.52                 | 83.17                | 1683.27  |
