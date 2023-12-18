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

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch
Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

### Use smaller models

You can use smaller model `BAAI/bge-small-en-v1.5` (`MODEL_EN_BGE_SMALL`) to speed up the scanner. It is 4 times faster
than the default model, but it is less accurate.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Relevance
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge                    | 22           | 5          | 2.95             | 196.86                | 223.97                | 245.66                | 142.39               | 154.51 |
| AWS m5.xlarge with ONNX          | 22           | 5          | 0.25             | 52.00                 | 59.90                 | 66.23                 | 35.92                | 612.47 |
| AWS g5.xlarge GPU                | 22           | 5          | 28.59            | 269.77                | 354.29                | 421.90                | 100.63               | 218.62 |
| Azure Standard_D4as_v4           | 22           | 5          | 3.95             | 224.87                | 255.90                | 280.73                | 161.19               | 136.48 |
| Azure Standard_D4as_v4 with ONNX | 22           | 5          | 0.01             | 52.61                 | 53.42                 | 54.07                 | 49.76                | 442.11 |
