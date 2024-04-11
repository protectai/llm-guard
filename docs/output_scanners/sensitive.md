# Sensitive Scanner

The Sensitive Scanner serves as your digital vanguard, ensuring that the language model's output is purged of Personally
Identifiable Information (PII) and other sensitive data, safeguarding user interactions.

## Attack scenario

ML/AI systems are prone to data leakage, which can occur at various stages of data processing, model training, or output generation, leading to unintended exposure of sensitive or proprietary information.

Data leakage in ML/AI systems encompasses more than unauthorized database access; it can occur subtly when models unintentionally expose information about their training data. For example, models that overfit may allow inferences about the data they were trained on, presenting challenging-to-detect risks of potential data breaches.

A data breach in an AI system can have severe consequences, including:

- Financial Impact: Data breaches can lead to significant fines and are particularly costly in heavily regulated industries or areas with strict data protection laws.
- Reputation Damage: Trust issues stemming from data leaks can affect relationships with clients, partners, and the wider stakeholder community, potentially resulting in lost business.
- Legal and Compliance Implications: Non-compliance with data protection can lead to legal repercussions and sanctions.
- Operational Impact: Breaches may interrupt business operations, requiring extensive efforts to resolve and recover from the incident.
- Intellectual Property Risks: Leaks in certain fields could disclose proprietary methodologies or trade secrets, offering competitors unfair advantages.

Referring to the `OWASP Top 10 for Large Language Model Applications`, this falls under: [LLM06: Sensitive Information Disclosure](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

Also, CWE has identified the following weaknesses that are related to this scanner:

- **CWE-200**: Exposure of Sensitive Information to an Unauthorized Actor: Denotes the risk of accidentally revealing sensitive data.
- **CWE-359**: Exposure of Private Personal Information (PPI): Highlights the dangers of leaking personal data.

## How it works

It uses mechanisms from the [Anonymize](../input_scanners/anonymize.md) scanner.

## Usage

Configure the scanner:

```python
from llm_guard.output_scanners import Sensitive

scanner = Sensitive(entity_types=["PERSON", "EMAIL"], redact=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

To enhance flexibility, users can introduce their patterns through the `regex_pattern_groups_path`.

The `redact` feature, when enabled, ensures sensitive entities are seamlessly replaced.

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 30
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output Sensitive
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 4.48             | 162.42                | 195.80                | 222.50                | 95.26                | 314.91  |
| AWS m5.xlarge with ONNX          | 0.23             | 75.19                 | 82.71                 | 88.72                 | 59.75                | 502.10  |
| AWS g5.xlarge GPU                | 33.82            | 290.10                | 381.92                | 455.38                | 105.93               | 283.20  |
| AWS g5.xlarge GPU with ONNX      | 0.41             | 39.55                 | 49.57                 | 57.59                 | 18.88                | 1589.04 |
| Azure Standard_D4as_v4           | 6.30             | 192.82                | 231.35                | 262.18                | 111.32               | 269.49  |
| Azure Standard_D4as_v4 with ONNX | 0.37             | 72.21                 | 80.89                 | 87.84                 | 51.49                | 582.65  |
