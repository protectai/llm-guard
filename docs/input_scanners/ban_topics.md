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

[Collection on HuggingFace](https://huggingface.co/collections/MoritzLaurer/zeroshot-classifiers-6548b4ff407bb19ff5c3ad6f)

## Usage

```python
from llm_guard.input_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## How to configure topics

The topics to be banned can be chosen based on the use-case and the potential risks associated with it.

The dataset, which was used to train the zero-shot classifier model can be found [here](https://huggingface.co/datasets/MoritzLaurer/synthetic_zeroshot_mixtral_v0.1).
It will give you an idea of the topics that the model can classify.

Additionally, we recommend experimenting with the formulating of the topics to choose the longer options ([Read more](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v2.0#flexible-usage-and-prompting)).

## Optimization Strategies

[Read more](../tutorials/optimization.md)

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

| Instance                       | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|--------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                  | 2.99             | 471.60                | 498.70                | 520.39                | 416.47               | 240.11  |
| AWS m5.xlarge with ONNX        | 0.11             | 135.12                | 139.92                | 143.77                | 123.71               | 808.31  |
| AWS g5.xlarge GPU              | 30.46            | 309.26                | 396.40                | 466.11                | 134.50               | 743.47  |
| AWS g5.xlarge GPU with ONNX    | 0.13             | 33.88                 | 39.43                 | 43.87                 | 22.38                | 4467.55 |
| AWS r6a.xlarge (AMD)           | 0.02             | 431.84                | 433.06                | 434.04                | 426.87               | 234.26  |
| AWS r6a.xlarge (AMD) with ONNX | 0.08             | 114.60                | 118.97                | 122.47                | 105.69               | 946.14  |
