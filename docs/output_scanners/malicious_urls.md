# Malicious URLs Scanner

This scanner detects URLs in the output and analyzes them for harmfulness, such as detecting phishing websites.

## Attack scenario

Large language models (LLMs) like GPT-4 are immensely sophisticated and have been trained on vast quantities of data
from the internet. This extensive training, while enabling them to generate coherent and contextually relevant
responses, also introduces certain risks. One of these risks is the inadvertent generation of malicious URLs in their
output.

## How it works

The scanner uses
the [DunnBC22/codebert-base-Malicious_URLs](https://huggingface.co/DunnBC22/codebert-base-Malicious_URLs) model from
HuggingFace to evaluate the security of a given URL.

The model provides a score between 0 and 1 for a URL being malware. This score is then compared against a pre-set
threshold to determine if the website is malicious. A score above the threshold suggests a malware link.

## Usage

```python
from llm_guard.output_scanners import MaliciousURLs

scanner = MaliciousURLs(threshold=0.7)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 51
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output MaliciousURLs
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 2.28             | 170.71                | 193.44                | 211.62                | 120.92               | 421.78  |
| AWS m5.xlarge with ONNX          | 0.09             | 81.78                 | 86.39                 | 90.09                 | 72.42                | 704.18  |
| AWS g5.xlarge GPU                | 28.80            | 270.73                | 355.51                | 423.34                | 100.89               | 505.5   |
| AWS g5.xlarge GPU with ONNX      | 0.11             | 21.36                 | 26.50                 | 30.61                 | 11.04                | 4620.81 |
| Azure Standard_D4as_v4           | 3.80             | 205.43                | 236.05                | 260.55                | 143.34               | 355.80  |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 54.65                 | 54.88                 | 55.08                 | 51.96                | 981.54  |
| AWS r6a.xlarge (AMD)             | 0.00             | 87.10                 | 87.70                 | 88.19                 | 84.73                | 601.90  |
| AWS r6a.xlarge (AMD) with ONNX   | 0.07             | 43.17                 | 47.26                 | 50.54                 | 34.89                | 1461.82 |
