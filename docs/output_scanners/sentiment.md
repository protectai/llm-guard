# Sentiment Scanner

The Sentiment Scanner is designed to scan and assess the sentiment of generated outputs. It leverages
the `SentimentIntensityAnalyzer` from the NLTK (Natural Language Toolkit) library to accomplish this.

## Attack scenario

By identifying texts with sentiment scores that deviate significantly from neutral, platforms can monitor and moderate
output sentiment, ensuring constructive and positive interactions.

## How it works

The sentiment score is calculated using nltk's `Vader` sentiment analyzer. The `SentimentIntensityAnalyzer` produces a
sentiment score ranging from -1 to 1:

- -1 represents a completely negative sentiment.
- 0 represents a neutral sentiment.
- 1 represents a completely positive sentiment.

By setting a predefined threshold, the scanner can be calibrated to flag any outputs falling below that threshold,
indicating a potentially negative sentiment.

## Usage

```python
from llm_guard.output_scanners import Sentiment

scanner = Sentiment(threshold=0)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

For a deeper understanding of the sentiment analysis process and its underlying methods, consult:

- [NLTK's Sentiment Analysis Guide](https://www.nltk.org/howto/sentiment.html)

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Sentiment
```

Results:

| Instance               | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS       |
|------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|-----------|
| AWS m5.xlarge          | 61           | 5          | 0.00             | 0.21                  | 0.22                  | 0.24                  | 0.16                 | 374752.26 |
| AWS g5.xlarge          | 61           | 5          | 0.00             | 0.18                  | 0.19                  | 0.20                  | 0.15                 | 420189.48 |
| Azure Standard_D4as_v4 | 61           | 5          | 0.00             | 0.25                  | 0.26                  | 0.28                  | 0.20                 | 309683.66 |
