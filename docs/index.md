# LLM Guard - The Security Toolkit for LLM Interactions

LLM-Guard is a comprehensive tool designed to fortify the security of Large Language Models (LLMs).

## What is LLM Guard?

![LLM-Guard](./img/flow.png)

By offering sanitization, detection of harmful language, prevention of data leakage, and resistance against prompt
injection attacks, LLM-Guard ensures that your interactions with LLMs remain safe and secure.

[Demo](https://huggingface.co/spaces/laiyer/llm-guard-playground)

## Installation

Begin your journey with LLM Guard by downloading the package and acquiring the `en_core_web_trf` spaCy model (essential
for the [Anonymize](./input_scanners/anonymize.md) scanner):

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

- Get started with [ChatGPT and LLM Guard](https://github.com/laiyer-ai/llm-guard/blob/main/examples/openai.py).

## Roadmap

**General:**

- [x] Introduce support of GPU
- [x] Improve documentation by showing use-cases, benchmarks, etc
- [ ] Hosted version of LLM Guard
- [ ] Text statistics to provide on prompt and output
- [ ] Support more languages
- [ ] Accept multiple outputs instead of one to compare
- [ ] Support streaming mode

**Prompt Scanner:**

- [ ] Integrate with Perspective API for Toxicity scanner
- [ ] Develop language restricting scanner

**Output Scanner:**

- [ ] Develop output scanners for the format (e.g. max length, correct JSON, XML, etc)
- [ ] Develop factual consistency scanner
- [ ] Develop libraries hallucination scanner
- [ ] Develop libraries licenses scanner

## Contributing

Got ideas, feedback, or wish to contribute? We'd love to hear from you! [Email us](mailto:hello@laiyer.ai).

For detailed guidelines on contributions, kindly refer to our [contribution guide](https://github.com/laiyer-ai/llm-guard/blob/main/CONTRIBUTING.md).
