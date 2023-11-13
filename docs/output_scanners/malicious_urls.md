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

## Optimizations

### ONNX

The scanner can be optimized by using the ONNX converted
model [laiyer/codebert-base-Malicious_URLs-onnx](https://huggingface.co/laiyer/codebert-base-Malicious_URLs-onnx).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output MaliciousURLs
```

Results:

| Instance                | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|-------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge           | 51           | 5          | 2.28             | 170.71                | 193.44                | 211.62                | 120.92               | 421.78 |
| AWS m5.xlarge with ONNX | 51           | 5          | 0.09             | 81.78                 | 86.39                 | 90.09                 | 72.42                | 704.18 |
| AWS g5.xlarge           | 51           | 5          | 28.80            | 270.73                | 355.51                | 423.34                | 100.89               | 505.5  |
