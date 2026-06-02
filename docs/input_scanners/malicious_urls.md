# Malicious URLs Scanner

This scanner detects URLs in the prompt and analyzes them for harmfulness, such as detecting phishing websites.

## Attack scenario

User-supplied prompts can contain malicious URLs, whether typed directly by an end user or smuggled in through a
prompt-injection or social-engineering payload. If such a URL reaches the model, a downstream tool, a browsing agent,
or another user, it can lead to phishing, malware delivery, or defacement. Scanning the prompt before it is processed
lets the application reject or flag these URLs early.

## How it works

The scanner uses
the [DunnBC22/codebert-base-Malicious_URLs](https://huggingface.co/DunnBC22/codebert-base-Malicious_URLs) model from
HuggingFace to evaluate the security of each URL found in the prompt.

The model provides a score between 0 and 1 for a URL being malware. This score is then compared against a pre-set
threshold to determine if the website is malicious. A score above the threshold suggests a malware link.

## Usage

```python
from llm_guard.input_scanners import MaliciousURLs

scanner = MaliciousURLs(threshold=0.7)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Run the following script:

```sh
python benchmarks/run.py input MaliciousURLs
```
