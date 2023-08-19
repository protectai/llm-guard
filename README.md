![LLM-Guard](https://raw.githubusercontent.com/laiyer-ai/llm-guard/ae37aa651e3142a1d40dae8895818ec91396e268/docs/flow.png?raw=true)

# LLM Guard - The Security Toolkit for LLM Interactions

LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs). By offering
sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt injection and
jailbreak attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/v/llm-guard)](https://pypi.org/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard)](https://pepy.tech/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard/month)](https://pepy.tech/project/llm-guard)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/laiyer_ai.svg?style=social&label=Follow%20%40Laiyer_AI)](https://twitter.com/laiyer_ai)

**❤️ Proudly developed by the [Laiyer.ai](https://laiyer.ai/) team.**

## Installation

Begin your journey with LLM Guard by downloading the package and acquiring the `en_core_web_trf` spaCy model (essential
for the [Anonymize](./docs/input_scanners/anonymize.md) scanner):

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

- [Anonymize](docs/input_scanners/anonymize.md)
- [BanSubstrings](docs/input_scanners/ban_substrings.md)
- [BanTopics](docs/input_scanners/ban_topics.md)
- [Code](docs/input_scanners/code.md)
- [Jailbreak](docs/input_scanners/jailbreak.md)
- [PromptInjection](docs/input_scanners/prompt_injection.md)
- [Secrets](docs/input_scanners/secrets.md)
- [Sentiment](docs/input_scanners/sentiment.md)
- [TokenLimit](docs/input_scanners/token_limit.md)
- [Toxicity](docs/input_scanners/toxicity.md)

### Output scanners

- [BanSubstrings](docs/output_scanners/ban_substrings.md)
- [BanTopics](docs/output_scanners/ban_topics.md)
- [Code](docs/output_scanners/code.md)
- [Deanonymize](docs/output_scanners/deanonymize.md)
- [MaliciousURLs](docs/output_scanners/malicious_urls.md)
- [NoRefusal](docs/output_scanners/no_refusal.md)
- [Refutation](docs/output_scanners/refutation.md)
- [Regex](docs/output_scanners/regex.md)
- [Relevance](docs/output_scanners/relevance.md)
- [Sensitive](docs/output_scanners/sensitive.md)
- [Toxicity](docs/output_scanners/toxicity.md)

## Roadmap

**General:**

- [x] Calculate risk score from 0 to 1 for each scanner
- [ ] Improve speed of transformers

**Prompt Scanner:**

- [ ] Improve Jailbreak scanner
- [ ] Better anonymizer with improved secrets detection and entity recognition
- [ ] Use Perspective API for Toxicity scanner

**Output Scanner:**

- [ ] Develop Fact Checking scanner
- [ ] Develop Hallucination scanner
- [ ] Develop scanner to check if the output stays on the topic of the prompt.

## Contributing

Got ideas, feedback, or wish to contribute? We'd love to hear from you! [Email us](mailto:hello@laiyer.ai).

For detailed guidelines on contributions, kindly refer to our [contribution guide](./docs/CONTRIBUTING.md).
