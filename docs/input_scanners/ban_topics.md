# Ban Topics Scanner

This scanner is designed to restrict specific topics, such as religion, violence, from being introduced in the prompt using Zero-Shot classifier.

This ensures that interactions remain within acceptable boundaries and avoids potentially sensitive or controversial
discussions.

## Attack scenario

Certain topics, when used as prompts for Language Learning Models, can lead to outputs that might be deemed sensitive,
controversial, or inappropriate. By banning these topics, service providers can maintain the quality of interactions and
reduce the risk of generating responses that could lead to misunderstandings or misinterpretations.

## How it works

It relies on the capabilities of the following models:

- [MoritzLaurer/deberta-v3-base-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1)
- [MoritzLaurer/deberta-v3-large-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v1)

These models aid in identifying the underlying theme or topic of a prompt, allowing the scanner to cross-check it against
a list of banned topics.

## Usage

```python
from llm_guard.input_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

### Use smaller models

You can rely on base model variant (default) to reduce the latency and memory footprint.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input BanTopics
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge                    | 100          | 5          | 2.99             | 471.60                | 498.70                | 520.39                | 416.47               | 240.11 |
| AWS m5.xlarge with ONNX          | 100          | 5          | 0.11             | 135.12                | 139.92                | 143.77                | 123.71               | 808.31 |
| AWS g5.xlarge GPU                | 100          | 5          | 30.46            | 309.26                | 396.40                | 466.11                | 134.50               | 743.47 |
| Azure Standard_D4as_v4           | 100          | 5          | 4.00             | 518.30                | 547.49                | 570.85                | 450.78               | 221.84 |
| Azure Standard_D4as_v4 with ONNX | 100          | 5          | 0.02             | 135.58                | 136.72                | 137.63                | 131.06               | 763.04 |
