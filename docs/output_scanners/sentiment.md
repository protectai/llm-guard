# Sentiment Scanner

The Sentiment Scanner is designed to scan and assess the sentiment of generated outputs. It leverages
the `SentimentIntensityAnalyzer` from the NLTK (Natural Language Toolkit) library to accomplish this.

## Attack

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
