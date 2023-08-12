# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-

### Fixed
-

### Changed
- [Anonymize prompt scanner] Using the transformer based Spacy model `en_core_web_trf` ([reference](https://microsoft.github.io/presidio/analyzer/nlp_engines/spacy_stanza/))
- [Anonymize prompt scanner] Supporting faker for applicable entities instead of placeholder (`use_faker` parameter)
- [Jailbreak prompt scanner] Updated dataset with more examples, removed duplicates

### Removed
-

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
  - [Jailbreak](./llm_guard/input_scanners/jailbreak.py)
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
[0.0.3]: https://github.com/laiyer-ai/llm-guard/commits/v0.0.3
[0.0.2]: https://github.com/laiyer-ai/llm-guard/commits/v0.0.2
[0.0.1]: https://github.com/laiyer-ai/llm-guard/commits/v0.0.1
