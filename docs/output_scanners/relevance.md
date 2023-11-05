# Relevance Scanner

The `Relevance` Scanner ensures that a language model's output remains relevant and aligned with the given input prompt. By measuring the similarity between the input prompt and the output, the scanner provides a confidence score, indicating the contextual relevance of the response.

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

You can select an embedding model suited to your needs. By default, it uses [BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5).

```python
from llm_guard.output_scanners import Relevance

scanner = Relevance(threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization

You can use smaller model `BAAI/bge-small-en-v1.5` (`MODEL_EN_BGE_SMALL`) to speed up the scanner. It is 4 times faster than the default model, but it is less accurate.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Relevance
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.043         | 509.48                | 22                     |
| m5.large (AWS)    | 0.075         | 294.05                | 22                     |
