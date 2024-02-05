# Ban Topics Scanner

This scanner is designed to restrict specific topics, such as religion, violence, from being introduced in the prompt
using Zero-Shot classifier.

This ensures that interactions remain within acceptable boundaries and avoids potentially sensitive or controversial
discussions.

## Attack scenario

Certain topics, when used as prompts for Language Learning Models, can lead to outputs that might be deemed sensitive,
controversial, or inappropriate. By banning these topics, service providers can maintain the quality of interactions and
reduce the risk of generating responses that could lead to misunderstandings or misinterpretations.

## How it works

It relies on the capabilities of the following models to perform zero-shot classification:

| Model                                                                                                                                   | Description                                                                                                                                                                                                                                |
|-----------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33)         | It was trained on a mixture of 33 datasets and 389 classes reformatted in the universal NLI format. The model is English only. You can also use it for multilingual zeroshot classification by first machine translating texts to English. |
| [MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33)           | This is essentially the same as its larger sister only that it's smaller. Use it if you need more speed. The model is English-only.                                                                                                        |
| [MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33)       | Same as above, just smaller/faster.                                                                                                                                                                                                        |
| [MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33) | Same as above, just even faster. The model only has 22 million backbone parameters. The model is 25 MB small (or 13 MB with ONNX quantization).                                                                                            |

## Usage

```python
from llm_guard.input_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

[Read more](../usage/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 100
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input BanTopics
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 2.99             | 471.60                | 498.70                | 520.39                | 416.47               | 240.11  |
| AWS m5.xlarge with ONNX          | 0.11             | 135.12                | 139.92                | 143.77                | 123.71               | 808.31  |
| AWS g5.xlarge GPU                | 30.46            | 309.26                | 396.40                | 466.11                | 134.50               | 743.47  |
| AWS g5.xlarge GPU with ONNX      | 0.13             | 33.88                 | 39.43                 | 43.87                 | 22.38                | 4467.55 |
| Azure Standard_D4as_v4           | 4.00             | 518.30                | 547.49                | 570.85                | 450.78               | 221.84  |
| Azure Standard_D4as_v4 with ONNX | 0.02             | 135.58                | 136.72                | 137.63                | 131.06               | 763.04  |
