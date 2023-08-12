# Malicious URLs Scanner

This scanner leverages a pre-trained model from HuggingFace to detect harmful URLs, such as phishing websites. The model
classifies URL addresses into two categories: 'malware' and 'benign'. The intent is to assess if a given URL is
malicious.

## Attack

Large language models (LLMs) like GPT-4 are immensely sophisticated and have been trained on vast quantities of data
from the internet. This extensive training, while enabling them to generate coherent and contextually relevant
responses, also introduces certain risks. One of these risks is the inadvertent generation of malicious URLs in their
output.

## How it works

The scanner uses the [elftsdmr/malware-url-detect](https://huggingface.co/elftsdmr/malware-url-detect) model from
HuggingFace to evaluate the security of a given URL.

For usage, only the domain name of the URL should be provided (e.g., "huggingface.com").

The model provides a score between 0 and 1 for a URL being malware. This score is then compared against a pre-set
threshold to determine if the website is malicious. A score above the threshold suggests a malware link.

## Usage

```python
from llm_guard.output_scanners import MaliciousURLs

scanner = MaliciousURLs(threshold=0.7)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
