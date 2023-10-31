# Secrets Scanner

This scanner diligently examines user inputs, ensuring that they don't carry any secrets before they are processed by
the language model.

## Attack

Large Language Models (LLMs), when provided with user inputs containing secrets or sensitive information, might
inadvertently generate responses that expose these secrets. This can be a significant security concern as this sensitive
data, such as API keys or passwords, could be misused if exposed.

To counteract this risk, we employ the Secrets scanner. It ensures that user prompts are meticulously scanned and any
detected secrets are redacted before they are processed by the model.

## Usage

While communicating with LLMs, the scanner acts as a protective layer, ensuring that your sensitive data remains
confidential.

This scanner leverages the capabilities of the [detect-secrets](https://github.com/Yelp/detect-secrets) library, a tool
engineered by Yelp, to meticulously detect secrets in strings of text.

### Types of secrets

- API Tokens (e.g., AWS, Azure, GitHub, Slack)
- Private Keys
- High Entropy Strings (both Base64 and Hex)
  ... and [many more](https://github.com/Yelp/detect-secrets/blob/master/README.md#viewing-all-enabled-plugins)

### Getting started

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

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.081         | 741.52                | 60                     |
| m5.large (AWS)    | 0.093         | 646.87                | 60                     |
