# LLM Guard - The Security Toolkit for LLM Interactions

LLM Guard by [Laiyer.ai](https://laiyer.ai) is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

[**Documentation**](https://laiyer-ai.github.io/llm-guard/) | [**Demo**](https://huggingface.co/spaces/laiyer/llm-guard-playground)

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

![LLM-Guard](https://raw.githubusercontent.com/laiyer-ai/llm-guard/ddba0d6f696ca539628c04bc81978b07e3d4ccb9/docs/img/flow.png?raw=true)

By offering sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt
injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

## Installation

Begin your journey with LLM Guard by downloading the package:

```sh
pip install llm-guard
```

And then download a preferred spaCy model for [Anonymize](https://laiyer-ai.github.io/llm-guard/input_scanners/anonymize/) scanner. By default, you can use:

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

- Get started with [ChatGPT and LLM Guard](./examples/openai.py).

## Supported scanners

### Prompt scanners

- [Anonymize](https://laiyer-ai.github.io/llm-guard/input_scanners/anonymize/)
- [BanSubstrings](https://laiyer-ai.github.io/llm-guard/input_scanners/ban_substrings/)
- [BanTopics](https://laiyer-ai.github.io/llm-guard/input_scanners/ban_topics/)
- [Code](https://laiyer-ai.github.io/llm-guard/input_scanners/code/)
- [Language](https://laiyer-ai.github.io/llm-guard/input_scanners/language/)
- [PromptInjection](https://laiyer-ai.github.io/llm-guard/input_scanners/prompt_injection/)
- [Regex](https://laiyer-ai.github.io/llm-guard/input_scanners/regex/)
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
- [JSON](https://laiyer-ai.github.io/llm-guard/output_scanners/json/)
- [Language](https://laiyer-ai.github.io/llm-guard/output_scanners/language/)
- [LanguageSame](https://laiyer-ai.github.io/llm-guard/output_scanners/language_same/)
- [MaliciousURLs](https://laiyer-ai.github.io/llm-guard/output_scanners/malicious_urls/)
- [NoRefusal](https://laiyer-ai.github.io/llm-guard/output_scanners/no_refusal/)
- [Refutation](https://laiyer-ai.github.io/llm-guard/output_scanners/refutation/)
- [Regex](https://laiyer-ai.github.io/llm-guard/output_scanners/regex/)
- [Relevance](https://laiyer-ai.github.io/llm-guard/output_scanners/relevance/)
- [Sensitive](https://laiyer-ai.github.io/llm-guard/output_scanners/sensitive/)
- [Sentiment](https://laiyer-ai.github.io/llm-guard/output_scanners/sentiment/)
- [Toxicity](https://laiyer-ai.github.io/llm-guard/output_scanners/toxicity/)

## Roadmap

You can find our roadmap [here](https://llm-guard.com/#roadmap). Please don't hesitate to contribute or create issues, it helps us improve LLM Guard!

## Contributing

Got ideas, feedback, or wish to contribute? We'd love to hear from you! [Email us](mailto:hello@laiyer.ai).

For detailed guidelines on contributions, kindly refer to our [contribution guide](CONTRIBUTING.md).
