# LLM Guard - The Security Toolkit for LLM Interactions

LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

[**Documentation**](https://laiyer-ai.github.io/llm-guard/) | [**Demo**](https://huggingface.co/spaces/laiyer/llm-guard-playground)

[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/v/llm-guard)](https://pypi.org/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard)](https://pepy.tech/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard/month)](https://pepy.tech/project/llm-guard)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/laiyer_ai.svg?style=social&label=Follow%20%40Laiyer_AI)](https://twitter.com/laiyer_ai)

**❤️ Proudly developed by the [Laiyer.ai](https://laiyer.ai/) team.**

## What is LLM Guard?

![LLM-Guard](https://raw.githubusercontent.com/laiyer-ai/llm-guard/ddba0d6f696ca539628c04bc81978b07e3d4ccb9/docs/img/flow.png?raw=true)

By offering sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt
injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

## Installation

Begin your journey with LLM Guard by downloading the package and acquiring the `en_core_web_trf` spaCy model (essential
for the [Anonymize](https://laiyer-ai.github.io/llm-guard/input_scanners/anonymize/) scanner):

```sh
pip install llm-guard
python -m spacy download en_core_web_trf
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

- Get started with [ChatGPT and LLM Guard](./examples/openai.py).

## Supported scanners

### Prompt scanners

- [Anonymize](https://laiyer-ai.github.io/llm-guard/input_scanners/anonymize/)
- [BanSubstrings](https://laiyer-ai.github.io/llm-guard/input_scanners/ban_substrings/)
- [BanTopics](https://laiyer-ai.github.io/llm-guard/input_scanners/ban_topics/)
- [Code](https://laiyer-ai.github.io/llm-guard/input_scanners/code/)
- [PromptInjection](https://laiyer-ai.github.io/llm-guard/input_scanners/prompt_injection/)
- [Secrets](https://laiyer-ai.github.io/llm-guard/input_scanners/secrets/)
- [Sentiment](https://laiyer-ai.github.io/llm-guard/input_scanners/sentiment/)
- [TokenLimit](https://laiyer-ai.github.io/llm-guard/input_scanners/token_limit/)
- [Toxicity](https://laiyer-ai.github.io/llm-guard/input_scanners/toxicity/)

### Output scanners

- [BanSubstrings](https://laiyer-ai.github.io/llm-guard/output_scanners/ban_substrings/)
- [BanTopics](https://laiyer-ai.github.io/llm-guard/output_scanners/ban_topics/)
- [Bias](https://laiyer-ai.github.io/llm-guard/output_scanners/bias/)
- [Code](https://laiyer-ai.github.io/llm-guard/output_scanners/code/)
- [Deanonymize](https://laiyer-ai.github.io/llm-guard/output_scanners/deanonymize/)
- [MaliciousURLs](https://laiyer-ai.github.io/llm-guard/output_scanners/malicious_urls/)
- [NoRefusal](https://laiyer-ai.github.io/llm-guard/output_scanners/no_refusal/)
- [Refutation](https://laiyer-ai.github.io/llm-guard/output_scanners/refutation/)
- [Regex](https://laiyer-ai.github.io/llm-guard/output_scanners/regex/)
- [Relevance](https://laiyer-ai.github.io/llm-guard/output_scanners/relevance/)
- [Sensitive](https://laiyer-ai.github.io/llm-guard/output_scanners/sensitive/)
- [Sentiment](https://laiyer-ai.github.io/llm-guard/output_scanners/sentiment/)
- [Toxicity](https://laiyer-ai.github.io/llm-guard/output_scanners/toxicity/)

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

For detailed guidelines on contributions, kindly refer to our [contribution guide](CONTRIBUTING.md).
