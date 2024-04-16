# Ban Topics Scanner

This scanner is designed to detect outputs that touch upon topics that are considered sensitive using Zero-Shot
classifier.

## Attack scenario

Even with controlled prompts, LLMs might produce outputs touching upon themes or subjects that are considered sensitive,
controversial, or outside the scope of intended interactions. Without preventive measures, this can lead to outputs that
are misaligned with the platform's guidelines or values.

## How it works

It relies on the capabilities of the following models to perform zero-shot classification:

[Collection on HuggingFace](https://huggingface.co/collections/MoritzLaurer/zeroshot-classifiers-6548b4ff407bb19ff5c3ad6f)

## Usage

```python
from llm_guard.output_scanners import BanTopics

scanner = BanTopics(topics=["violence"], threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## How to configure topics

The topics to be banned can be chosen based on the use-case and the potential risks associated with it.

The dataset, which was used to train the zero-shot classifier model can be found [here](https://huggingface.co/datasets/MoritzLaurer/synthetic_zeroshot_mixtral_v0.1).
It will give you an idea of the topics that the model can classify.

Additionally, we recommend experimenting with the formulating of the topics to choose the longer options ([Read more](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v2.0#flexible-usage-and-prompting)).

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output BanTopics
```

Results:

| Instance                         | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 5          | 2.39             | 485.00                | 509.32                | 528.78                | 435.82               | 204.21  |
| AWS m5.xlarge with ONNX          | 5          | 0.09             | 165.61                | 170.05                | 173.60                | 155.90               | 570.87  |
| AWS g5.xlarge GPU                | 5          | 35.44            | 331.25                | 425.26                | 500.46                | 142.77               | 623.37  |
| AWS g5.xlarge GPU with ONNX      | 5          | 0.13             | 33.26                 | 38.89                 | 43.40                 | 21.76                | 4090.94 |
| Azure Standard_D4as_v4           | 5          | 3.91             | 547.06                | 577.87                | 602.53                | 483.73               | 183.99  |
| Azure Standard_D4as_v4 with ONNX | 5          | 0.06             | 176.34                | 179.65                | 182.30                | 168.16               | 529.25  |
