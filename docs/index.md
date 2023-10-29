# LLM Guard - The Security Toolkit for LLM Interactions

LLM Guard by [Laiyer.ai](https://laiyer.ai) is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

## What is LLM Guard?

![LLM-Guard](./img/flow.png)

By offering sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt
injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

[Demo](https://huggingface.co/spaces/laiyer/llm-guard-playground)

## Installation

Begin your journey with LLM Guard by downloading the package:

```sh
pip install llm-guard
```

And then download a preferred spaCy model for [Anonymize](./input_scanners/anonymize.md) scanner. By default, you can use:

```sh
pip install https://huggingface.co/beki/en_spacy_pii_distilbert/resolve/main/en_spacy_pii_distilbert-any-py3-none-any.whl
```

## Getting Started

**Important Notes**:

- LLM Guard is designed for easy integration and deployment in production environments. While it's ready to use
  out-of-the-box, please be informed that we're constantly improving and updating the repository.
- Base functionality requires a limited number of libraries. As you explore more advanced features, necessary libraries
  will be automatically installed.
- Ensure you're using Python version 3.8.1 or higher. Confirm with: `python --version`.
- Library installation issues? Consider upgrading pip: `python -m pip install --upgrade pip`.

**Examples**:

- Get started with [ChatGPT and LLM Guard](https://github.com/laiyer-ai/llm-guard/blob/main/examples/openai_api.py).

## Roadmap

### General

- [ ] Extend language support to cover popular and emerging languages, prioritize based on community feedback.
- [ ] Allow comparison of multiple outputs to facilitate better analysis and choice.
- [ ] Enable scanning of logits to support streaming mode.
- [ ] Expand examples and integrations, ensuring they cover common use-cases and are easy to follow.

### Latency

- [ ] Implement parallel scanning using multiprocessing to significantly reduce scanning time.
- [ ] Provide an option to utilize lighter models for quicker scanning, while maintaining an acceptable level of accuracy.
- [ ] Incorporate LRU cache to optimize performance by reusing previous results where applicable.

### Prompt Scanners

- [ ] Allow language restriction to focus scanning efforts and improve accuracy.
- [ ] Utilize expressions for code detection to reduce dependency on models, improving speed and reliability.
- [ ] Integrate yara for secret detection to enhance security scanning capabilities.
- [ ] Sanitize text.
- [ ] Support a variety of token calculators to offer more flexibility and compatibility.

### Output Scanners

- [ ] Sanitize text to maintain a clean, accurate scanning process.
- [ ] Validate output formats like JSON, XML to ensure they adhere to standards.
- [ ] Incorporate factual consistency checking to uphold the reliability of the data.
- [ ] Scan for vulnerable libraries and provide recommendations for safer alternatives.
- [ ] Check for license compliance to ensure legal integrity.
- [ ] Detect insecure code patterns.
- [ ] Identify potential SQL injection points to enhance security.
- [ ] Verify links and provide options for whitelisting or blacklisting to maintain the quality of references.

## Contributing

Got ideas, feedback, or wish to contribute? We'd love to hear from you! [Email us](mailto:hello@laiyer.ai).

For detailed guidelines on contributions, kindly refer to our [contribution guide](https://github.com/laiyer-ai/llm-guard/blob/main/CONTRIBUTING.md).
