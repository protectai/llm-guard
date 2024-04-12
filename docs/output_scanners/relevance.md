# Relevance Scanner

This scanner ensures that output remains relevant and aligned with the given input prompt.

By measuring the similarity between the input prompt and the output, the scanner provides a confidence score, indicating
the contextual relevance of the response.

## How it works

1. The scanner translates both the prompt and the output into vector embeddings.
2. It calculates the cosine similarity between these embeddings.
3. This similarity score is then compared against a predefined threshold to determine contextual relevance.

**Example:**

- **Prompt**: What is the primary function of the mitochondria in a cell?
- **Output**: The Eiffel Tower is a renowned landmark in Paris, France
- **Valid**: False

The scanner leverages the [best available embedding model](https://huggingface.co/spaces/mteb/leaderboard).

## Usage

You can select an embedding model suited to your needs. By default, it
uses [BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5).

```python
from llm_guard.output_scanners import Relevance

scanner = Relevance(threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 22
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output Relevance
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge                    | 2.95             | 196.86                | 223.97                | 245.66                | 142.39               | 154.51 |
| AWS m5.xlarge with ONNX          | 0.25             | 52.00                 | 59.90                 | 66.23                 | 35.92                | 612.47 |
| AWS g5.xlarge GPU                | 28.59            | 269.77                | 354.29                | 421.90                | 100.63               | 218.62 |
| AWS g5.xlarge GPU with ONNX      | 0.03             | 42.50                 | 45.18                 | 47.32                 | 37.14                | 592.43 |
| Azure Standard_D4as_v4           | 3.95             | 224.87                | 255.90                | 280.73                | 161.19               | 136.48 |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 52.61                 | 53.42                 | 54.07                 | 49.76                | 442.11 |
| AWS r6a.xlarge (AMD)             | 0.00             | 95.34                 | 96.25                 | 96.98                 | 93.23                | 235.97 |
| AWS r6a.xlarge (AMD) with ONNX   | 0.17             | 54.63                 | 61.07                 | 66.22                 | 41.71                | 527.50 |
