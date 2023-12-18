# Secrets Scanner

This scanner diligently examines user inputs, ensuring that they don't carry any secrets before they are processed by
the language model.

## Attack scenario

Large Language Models (LLMs), when provided with user inputs containing secrets or sensitive information, might
inadvertently generate responses that expose these secrets. This can be a significant security concern as this sensitive
data, such as API keys or passwords, could be misused if exposed.

To counteract this risk, we employ the Secrets scanner. It ensures that user prompts are meticulously scanned and any
detected secrets are redacted before they are processed by the model.

## How it works

While communicating with LLMs, the scanner acts as a protective layer, ensuring that your sensitive data remains
confidential.

This scanner leverages the capabilities of the [detect-secrets](https://github.com/Yelp/detect-secrets) library, a tool
engineered by Yelp, to meticulously detect secrets in strings of text.

### Types of secrets

- API Tokens (e.g., AWS, Azure, GitHub, Slack)
- Private Keys
- High Entropy Strings (both Base64 and Hex)
  ... and [many more](https://github.com/Yelp/detect-secrets/blob/master/README.md#viewing-all-enabled-plugins)

### Usage

```python
from llm_guard.input_scanners import Secrets

scanner = Secrets(redact_mode=Secrets.REDACT_PARTIAL)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

Here's what those options do:

- `detect_secrets_config`: This allows for a custom configuration for the `detect-secrets` library.
- `redact_mode`: It defines how the detected secrets will be redacted—options include partial redaction, complete
  hiding, or replacing with a hash.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input Secrets
```

Results:

| Instance               | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge          | 60           | 5          | 2.92             | 83.84                 | 110.85                | 132.45                | 29.75                | 2016.83 |
| AWS g5.xlarge GPU      | 60           | 5          | 3.34             | 89.20                 | 118.11                | 141.23                | 31.39                | 1911.67 |
| Azure Standard_D4as_v4 | 60           | 5          | 5.46             | 114.56                | 180.92                | 40.56                 | 421.46               | 1479.37 |
