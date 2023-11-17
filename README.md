# LLM Guard - The Security Toolkit for LLM Interactions

LLM Guard by [Laiyer.ai](https://laiyer.ai) is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

[**Documentation**](https://laiyer-ai.github.io/llm-guard/) | [**Playground**](https://huggingface.co/spaces/laiyer/llm-guard-playground) | [**Changelog**](https://llm-guard.com/changelog/) | [**Blog**](https://substack.com/@laiyer) | [**Slack**](https://join.slack.com/t/laiyerai/shared_invite/zt-26i905g3a-dB2~3~EkETRobSqe3PUbNA)

[![GitHub
stars](https://img.shields.io/github/stars/laiyer-ai/llm-guard.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/laiyer-ai/llm-guard/stargazers/)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/v/llm-guard)](https://pypi.org/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard)](https://pepy.tech/project/llm-guard)
[![Downloads](https://static.pepy.tech/badge/llm-guard/month)](https://pepy.tech/project/llm-guard)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/laiyer_ai.svg?style=social&label=Follow%20%40Laiyer_AI)](https://twitter.com/laiyer_ai)

## What is LLM Guard?

![LLM-Guard](https://github.com/laiyer-ai/llm-guard/blob/main/docs/assets/flow.png?raw=true)

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
- Ensure you're using Python version 3.9 or higher. Confirm with: `python --version`.
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

## Community, Contributing, Docs & Support

LLM Guard is an open source solution.
We are committed to a transparent development process and highly appreciate any contributions.
Whether you are helping us fix bugs, propose new features, improve our documentation or spread the word,
we would love to have you as part of our community.

- Give us a ⭐️ github star ⭐️ on the top of this page to support what we're doing,
  it means a lot for open source projects!
- Read our
  [docs](https://laiyer-ai.github.io/llm-guard/)
  for more info about how to use and customize LLM Guard, and for step-by-step tutorials.
- Post a [Github
  Issue](https://github.com/laiyer-ai/llm-guard/issues) to submit a bug report, feature request, or suggest an improvement.
- To contribute to the package, check out our [contribution guidelines](CONTRIBUTING.md), and open a PR.

Join our Slack to give us feedback, connect with the maintainers and fellow users, ask questions,
get help for package usage or contributions, or engage in discussions about LLM security!

<a href="https://join.slack.com/t/laiyerai/shared_invite/zt-26i905g3a-dB2~3~EkETRobSqe3PUbNA"><img src="https://github.com/laiyer-ai/llm-guard/blob/main/docs/assets/join-our-slack-community.png?raw=true" width="200"></a>

### Production Support

We're eager to provide personalized assistance when deploying your LLM Guard to a production environment.

- [Send Email ✉️](mailto:hello@laiyer.ai)
