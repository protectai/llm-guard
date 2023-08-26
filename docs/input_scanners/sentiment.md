# Sentiment Scanner

It scans and evaluates the overall sentiment of prompts using the `SentimentIntensityAnalyzer` from the NLTK (Natural
Language Toolkit) library.

## Attack

The primary objective of the scanner is to gauge the sentiment of a given prompt. Prompts with sentiment scores below a
specified threshold are identified as having a negative sentiment. This can be especially useful in platforms where
monitoring and moderating user sentiment is crucial.

## How it works

The sentiment score is calculated using nltk's `Vader` sentiment analyzer. The `SentimentIntensityAnalyzer` produces a sentiment score ranging from -1 to 1:

- -1 represents a completely negative sentiment.
- 0 represents a neutral sentiment.
- 1 represents a completely positive sentiment.

By setting a predefined threshold, the scanner can be calibrated to flag any prompts falling below that threshold,
indicating a potentially negative sentiment.

## Usage

```python
from llm_guard.input_scanners import Sentiment

scanner = Sentiment(threshold=0)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

For a deeper understanding of the sentiment analysis process and its underlying methods, consult:

- [NLTK's Sentiment Analysis Guide](https://www.nltk.org/howto/sentiment.html)
