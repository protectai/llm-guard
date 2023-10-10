# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `Regex` scanner to the prompt
- `Language` scanners both for prompt and output
- `JSON` output scanner
- Best practices to the documentation
- `LanguageSame` output scanner to check that the prompt and output languages are the same

### Fixed
-

### Changed
- `BanSubstrings` can match all substrings in addition to any of them
- `Sensitive` output scanner can redact found entities
- Change to faster model for `BanTopics` prompt and output scanners [MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c)
- Changed model for the 'NoRefusal' scanner to faster [MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c)

### Removed
-

## [0.2.4] - 2023-10-07

### Added
- Langchain [example](examples/langchain_lcel.py) using [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/)
- Added prompt injection scanner v2 model based on [hubert233/GPTFuzz](https://huggingface.co/hubert233/GPTFuzz)

### Changed
- Using another Bias detection model which works better on different devices [valurank/distilroberta-bias](https://huggingface.co/valurank/distilroberta-bias)
- Updated the roadmap in README and documentation
- `BanSubstrings` can redact found substrings
- One `logger` for all scanners
- `device` became function to lazy load (avoid `torch` import when unnecessary)
- Lazy load dependencies in scanners
- Added elapsed time in logs of `evaluate_prompt` and `evaluate_output` functions
- New secrets detectors
- Added GPU benchmarks on `g5.xlarge` instance
- Tests are running on Python 3.9, 3.10 and 3.11

### Removed
- Usage of `accelerate` library for inference. Instead, it will detect device using `torch`

## [0.2.3] - 2023-09-23

### Changed
- Added Swagger documentation on the [API](https://llm-guard.com/usage/api/) documentation page
- Added `fail_fast` flag to stop the execution after the first failure
  - Updated API and Playground to support `fail_fast` flag
  - Clarified order of execution in the documentation
- Added timeout configuration for API example
- Better examples of `langchain` integration

## [0.2.2] - 2023-09-21

### Fixed
- Missing secrets detection for Github token in the final build

## [0.2.1] - 2023-09-21

### Added
- New pages in the docs about usage of LLM Guard
- Benchmark of AWS EC2 `inf1.xlarge` instance
- Example of API with Docker in [examples/api](examples/api)
- `Regex` output scanner can redact the text using a regular expression

### Changed
- Lowercase prompt in Relevance output scanner to improve quality of cosine similarity
- Detect code snippets from Markdown in `Code` scanner to prevent false-positives
- Changed model used for `PromptInjection` to `JasperLS/deberta-v3-base-injection`, which produces less false-positives
- Introduced `threshold` parameter for `Code` scanners to control the threshold for the similarity

## [0.2.0] - 2023-09-15

### Added
- Documentation moved to `mkdocs`
- Benchmarks in the documentation
- Added documentation about [adding more scanners](docs/add_scanner.md)
- `Makefile` with useful commands
- Demo application using Streamlit deployed to HuggingFace Spaces

### Fixed
- `MaliciousURLs` scanner produced false positives when URLs are not extracted from the text

### Changed
- Support of GPU inference
- Score of existing `Anonymize` patterns

### Removed
- `URL` entity type from `Anonymize` scanner (it was producing false-positive results)

## [0.1.3] - 2023-09-02

### Changed
- Lock `transformers` version to 4.32.0 because `spacy-transformers` require it
- Update the roadmap based on the feedback from the community
- Updated `NoRefusal` scanner to use transformer to classify the output

### Removed
- Jailbreak input scanner (it was doing the same as the prompt injection one)

## [0.1.2] - 2023-08-26

### Added
- [Bias output scanner](./docs/output_scanners/bias.md)
- [Sentiment output scanner](./docs/output_scanners/sentiment.md)

### Changed
- Introduced new linters for markdown

## [0.1.1] - 2023-08-20

### Added
- Example integration with [LangChain](https://github.com/langchain-ai/langchain)

### Changed
- Flow picture instead of the logo
- Bump libraries

## [0.1.0] - 2023-08-12

### Added
- [Refutation output scanner](./docs/output_scanners/refutation.md)
- [MaliciousURLs output scanner](./docs/output_scanners/malicious_urls.md)
- [Secrets prompt scanner](./docs/input_scanners/secrets.md)

### Changed
- **All prompt scanners**: Introducing a risk score, where 0 - means no risk, 1 - means high risk
- **All output scanners**: Introducing a risk score, where 0 - means no risk, 1 - means high risk
- **Anonymize prompt scanner**: Using the transformer based Spacy model `en_core_web_trf` ([reference](https://microsoft.github.io/presidio/analyzer/nlp_engines/spacy_stanza/))
- **Anonymize prompt scanner**: Supporting faker for applicable entities instead of placeholder (`use_faker` parameter)
- **Anonymize prompt scanner**: Remove all patterns for secrets detection, use [Secrets](docs/input_scanners/secrets.md) prompt scanner instead.
- **Jailbreak prompt scanner**: Updated dataset with more examples, removed duplicates

### Removed
- **Anonymize prompt scanner**: Removed `FILE_EXTENSION` entity type

## [0.0.3] - 2023-08-10

### Added
- Dependabot support
- CodeQL support
- More pre-commit hooks to improve linters

### Fixed
- Locked libraries in `requirements.txt`
- Logo link in README

## [0.0.2] - 2023-08-07

### Fixed

- Fixed missing `.json` files in the package

## [0.0.1] - 2023-08-07

### Added
- Project structure
- [Documentation](./README.md)
- Github Actions pipeline
- Prompt scanners with tests:
  - [Anonymize](./llm_guard/input_scanners/anonymize.py)
  - [BanSubstrings](./llm_guard/input_scanners/ban_substrings.py)
  - [BanTopics](./llm_guard/input_scanners/ban_topics.py)
  - [Code](./llm_guard/input_scanners/code.py)
  - [PromptInjection](./llm_guard/input_scanners/prompt_injection.py)
  - [Sentiment](./llm_guard/input_scanners/sentiment.py)
  - [TokenLimit](./llm_guard/input_scanners/token_limit.py)
  - [Toxicity](./llm_guard/input_scanners/toxicity.py)
- Output scanners with tests:
  - [BanSubstrings](./llm_guard/output_scanners/ban_substrings.py)
  - [BanTopics](./llm_guard/output_scanners/ban_topics.py)
  - [Code](./llm_guard/output_scanners/code.py)
  - [Deanonymize](./llm_guard/output_scanners/deanonymize.py)
  - [NoRefusal](./llm_guard/output_scanners/no_refusal.py)
  - [Regex](./llm_guard/output_scanners/regex.py)
  - [Relevance](./llm_guard/output_scanners/relevance.py)
  - [Sensitive](./llm_guard/output_scanners/sensitive.py)
  - [Toxicity](./llm_guard/output_scanners/toxicity.py)

[Unreleased]: https://github.com/laiyer-ai/llm-guard/commits/main
[0.2.4]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.2.4
[0.2.3]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.2.3
[0.2.2]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.2.2
[0.2.1]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.2.1
[0.2.0]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.2.0
[0.1.3]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.1.3
[0.1.2]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.1.2
[0.1.1]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.1.1
[0.1.0]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.1.0
[0.0.3]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.0.3
[0.0.2]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.0.2
[0.0.1]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.0.1
