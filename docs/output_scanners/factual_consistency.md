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

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch
Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output FactualConsistency
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 140          | 5          | 3.01             | 234.94                | 262.31                | 284.20                | 180.00               | 777.78  |
| AWS m5.xlarge with ONNX          | 140          | 5          | 0.09             | 98.62                 | 103.28                | 107.01                | 89.00                | 1573.02 |
| AWS g5.xlarge GPU                | 140          | 5          | 34.23            | 295.96                | 388.34                | 462.24                | 110.70               | 1264.69 |
| Azure Standard_D4as_v4           | 140          | 5          | 4.14             | 271.39                | 302.78                | 327.89                | 205.62               | 680.87  |
| Azure Standard_D4as_v4 with ONNX | 140          | 5          | 0.01             | 62.73                 | 63.71                 | 64.51                 | 59.82                | 2340.44 |
