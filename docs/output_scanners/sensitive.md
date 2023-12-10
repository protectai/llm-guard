# Sensitive Scanner

The Sensitive Scanner serves as your digital vanguard, ensuring that the language model's output is purged of Personally
Identifiable Information (PII) and other sensitive data, safeguarding user interactions.

## Attack

Language Learning Models (LLMs) occasionally pose the risk of unintentionally divulging sensitive information. The
consequences can range from privacy violations to considerable security threats. The Sensitive Scanner strives to
mitigate this by diligently scanning the model's responses.

Referring to the `OWASP Top 10 for Large Language Model Applications`, this falls under:

[LLM06: Sensitive Information Disclosure](https://owasp.org/www-project-top-10-for-large-language-model-applications/) -
To combat this, it's vital to integrate data sanitization and adopt strict user policies.

## How it works

It uses same mechanisms and de from the [Anonymize](../input_scanners/anonymize.md) scanner.

## Get started

Configure the scanner:

```python
from llm_guard.output_scanners import Sensitive

scanner = Sensitive(entity_types=["PERSON", "EMAIL"], redact=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

To enhance flexibility, users can introduce their patterns through the `regex_pattern_groups_path`.

The `redact` feature, when enabled, ensures sensitive entities are seamlessly replaced.

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

Make sure to install the `onnxruntime` package:

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
python benchmarks/run.py output Sensitive
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge                    | 30           | 5          | 4.48             | 162.42                | 195.80                | 222.50                | 95.26                | 314.91 |
| AWS m5.xlarge with ONNX          | 30           | 5          | 0.23             | 75.19                 | 82.71                 | 88.72                 | 59.75                | 502.10 |
| AWS g5.xlarge GPU                | 30           | 5          | 33.82            | 290.10                | 381.92                | 455.38                | 105.93               | 283.20 |
| Azure Standard_D4as_v4           | 30           | 5          | 6.30             | 192.82                | 231.35                | 262.18                | 111.32               | 269.49 |
| Azure Standard_D4as_v4 with ONNX | 30           | 5          | 0.37             | 72.21                 | 80.89                 | 87.84                 | 51.49                | 582.65 |
