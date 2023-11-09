# LLM Guard - The Security Toolkit for LLM Interactions

LLM Guard by [Laiyer.ai](https://laiyer.ai) is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

[**Documentation**](https://laiyer-ai.github.io/llm-guard/) | [**Demo**](https://huggingface.co/spaces/laiyer/llm-guard-playground) | [**Changelog**](https://llm-guard.com/changelog/)

[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/v/llm-guard)](https://pypi.org/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard)](https://pepy.tech/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard/month)](https://pepy.tech/project/llm-guard)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/laiyer_ai.svg?style=social&label=Follow%20%40Laiyer_AI)](https://twitter.com/laiyer_ai)

## Production Support / Help for companies

We're eager to provide personalized assistance when deploying your LLM Guard to a production environment.

- [Send Email ✉️](mailto:hello@laiyer.ai)

## What is LLM Guard?

![LLM-Guard](https://raw.githubusercontent.com/laiyer-ai/llm-guard/ddba0d6f696ca539628c04bc81978b07e3d4ccb9/docs/assets/flow.png?raw=true)

By offering sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt
injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

## Installation

Begin your journey with LLM Guard by downloading the package:

```sh
pip install llm-guard
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

- Get started with [ChatGPT and LLM Guard](./examples/openai_api.py).
- Deploy LLM Guard as [API](https://llm-guard.com/usage/api/)

## Supported scanners

### Prompt scanners

- [Anonymize](  https://llm-guard.com/input_scanners/anonymize/)
- [BanSubstrings](  https://llm-guard.com/input_scanners/ban_substrings/)
- [BanTopics](  https://llm-guard.com/input_scanners/ban_topics/)
- [Code](  https://llm-guard.com/input_scanners/code/)
- [Language](  https://llm-guard.com/input_scanners/language/)
- [PromptInjection](  https://llm-guard.com/input_scanners/prompt_injection/)
- [Regex](  https://llm-guard.com/input_scanners/regex/)
- [Secrets](  https://llm-guard.com/input_scanners/secrets/)
- [Sentiment](  https://llm-guard.com/input_scanners/sentiment/)
- [TokenLimit](  https://llm-guard.com/input_scanners/token_limit/)
- [Toxicity](  https://llm-guard.com/input_scanners/toxicity/)

### Output scanners

- [BanSubstrings](  https://llm-guard.com/output_scanners/ban_substrings/)
- [BanTopics](  https://llm-guard.com/output_scanners/ban_topics/)
- [Bias](  https://llm-guard.com/output_scanners/bias/)
- [Code](  https://llm-guard.com/output_scanners/code/)
- [Deanonymize](  https://llm-guard.com/output_scanners/deanonymize/)
- [JSON](  https://llm-guard.com/output_scanners/json/)
- [Language](  https://llm-guard.com/output_scanners/language/)
- [LanguageSame](  https://llm-guard.com/output_scanners/language_same/)
- [MaliciousURLs](  https://llm-guard.com/output_scanners/malicious_urls/)
- [NoRefusal](  https://llm-guard.com/output_scanners/no_refusal/)
- [FactualConsistency](  https://llm-guard.com/output_scanners/factual_consistency/)
- [Regex](  https://llm-guard.com/output_scanners/regex/)
- [Relevance](  https://llm-guard.com/output_scanners/relevance/)
- [Sensitive](  https://llm-guard.com/output_scanners/sensitive/)
- [Sentiment](  https://llm-guard.com/output_scanners/sentiment/)
- [Toxicity](  https://llm-guard.com/output_scanners/toxicity/)

## Roadmap

You can find our roadmap [here](https://llm-guard.com/#roadmap). Please don't hesitate to contribute or create issues, it helps us improve LLM Guard!

## Contributing

Got ideas, feedback, or wish to contribute? We'd love to hear from you! [Email us](mailto:hello@laiyer.ai).

For detailed guidelines on contributions, kindly refer to our [contribution guide](CONTRIBUTING.md).
