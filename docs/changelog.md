# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 0.3.4

### Added
-

### Fixed
-

### Changed
- Upgraded all libraries to the latest versions
- Improvements to the documentation

### Removed
-

## [0.3.3] - 2023-11-25

### Added
- Benchmarks on Azure instances

### Changed
- Upgraded `json_repair` library ([issue](https://github.com/laiyer-ai/llm-guard/issues/44))
- Use proprietary prompt injection detection model [laiyer/deberta-v3-base-prompt-injection](https://huggingface.co/laiyer/deberta-v3-base-prompt-injection)

## [0.3.2] - 2023-11-15

### Changed
- Using ONNX converted models hosted by Laiyer on HuggingFace
- Switched to better model for MaliciousURLs scanner - [DunnBC22/codebert-base-Malicious_URLs](https://huggingface.co/DunnBC22/codebert-base-Malicious_URLs)
- `BanTopics`, `NoRefusal`, `FactualConsistency` and `Relevance` scanners support ONNX inference
- `Relevance` rely on optimized ONNX models
- Switched to using `transformers` in `Relevance` scanner to have less dependencies
- Updated benchmarks for relevant scanners
- Use `papluca/xlm-roberta-base-language-detection` model for the `Language` and `LanguageSame` scanner
- `PromptInjection` calculates risk score based on the defined threshold
- Up-to-date Langchain integration using LCEL

### Removed
- Remove `lingua-language-detector` dependency from `Language` and `LanguageSame` scanners

## [0.3.1] - 2023-11-09

### Fixed
- Handling long prompts by truncating it to the maximum length of the model

### Changed
- Use single `PromptInjection` scanner with multiple models
- Benchmarks are measured for each scanner individually
- In the `Refutation` output scanner use the same model for the NLI as used in the `BanTopics`
- Benchmarks for each individual scanner instead of one common
- Use `deepset/deberta-v3-base-injection` model for the `PromptInjection` scanner
- Optimization of scanners on GPU by using `batch_size=1`
- Use `lingua-language-detector` instead of `langdetect` in the `Language` scanner
- Upgrade all libraries including `transformers` to the latest versions
- Use Transformers recognizers in the `Anonymize` and `Sensitive` scanner to improve named-entity recognition
- Possibility of using ONNX runtime in scanners by enabling `use_onnx` parameter
- Use the newest `MoritzLaurer/deberta-v3-base-zeroshot-v1` model for the `BanTopics` and `Refutation` scanners
- Use the newest `MoritzLaurer/deberta-v3-large-zeroshot-v1` model for the `NoRefusal` scanner
- Use better `unitary/unbiased-toxic-roberta` model for Toxicity scanners (both input and output)
- ONNX on API deployment for faster CPU inference
- CUDA on API deployment for faster GPU inference

### Removed
- Remove `PromptInjectionV2` scanner to rely on the single one with a choice
- Langchain `LLMChain` example as this functionality is deprecated, use `LCEL` instead

## [0.3.0] - 2023-10-14

### Added
- `Regex` scanner to the prompt
- `Language` scanners both for prompt and output
- `JSON` output scanner
- Best practices to the documentation
- `LanguageSame` output scanner to check that the prompt and output languages are the same

### Changed
- `BanSubstrings` can match all substrings in addition to any of them
- `Sensitive` output scanner can redact found entities
- Change to faster model for `BanTopics` prompt and output scanners [MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c)
- Changed model for the `NoRefusal` scanner to faster [MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c)
- `Anonymize` and `Sensitive` scanners support more accurate models (e.g. [beki/en_spacy_pii_distilbert](https://huggingface.co/beki/en_spacy_pii_distilbert) and ability to choose them. It also reduced the latency of this scanner
- Usage of `sentence-transformers` library replaced with `FlagEmbedding` in the `Relevance` output scanner
- Ability to choose embedding model in `Relevance` scanner and use the [best model](https://huggingface.co/spaces/mteb/leaderboard) currently available
- Cache tokenizers in memory to improve performance
- Moved API deployment to `llm_guard_api`
- `JSON` scanner can repair the JSON if it is broken
- Rename `Refutation` scanner to `FactualConsistency` to better reflect its purpose

### Removed
- Removed chunking in `Anonymize` and `Sensitive` scanners because it was breaking redaction

## [0.2.4] - 2023-10-07

### Added
- Langchain [example](https://github.com/laiyer-ai/llm-guard/blob/main/examples/langchain_lcel.py) using [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/)
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
- Added Swagger documentation on the [API](./usage/api.md) documentation page
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
- Example of API with Docker in [llm_guard_api](https://github.com/laiyer-ai/llm-guard/tree/main/llm_guard_api)
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
- Added documentation about [adding more scanners](./customization/add_scanner.md)
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
- [Bias output scanner](./output_scanners/bias.md)
- [Sentiment output scanner](./output_scanners/sentiment.md)

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
- [Refutation output scanner](./output_scanners/factual_consistency.md)
- [MaliciousURLs output scanner](./output_scanners/malicious_urls.md)
- [Secrets prompt scanner](./input_scanners/secrets.md)

### Changed
- **All prompt scanners**: Introducing a risk score, where 0 - means no risk, 1 - means high risk
- **All output scanners**: Introducing a risk score, where 0 - means no risk, 1 - means high risk
- **Anonymize prompt scanner**: Using the transformer based Spacy model `en_core_web_trf` ([reference](https://microsoft.github.io/presidio/analyzer/nlp_engines/spacy_stanza/))
- **Anonymize prompt scanner**: Supporting faker for applicable entities instead of placeholder (`use_faker` parameter)
- **Anonymize prompt scanner**: Remove all patterns for secrets detection, use [Secrets](./input_scanners/secrets.md) prompt scanner instead.
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
- [Documentation](./index.md)
- Github Actions pipeline
- Prompt scanners with tests:
  - [Anonymize](./input_scanners/anonymize.md)
  - [BanSubstrings](./input_scanners/ban_substrings.md)
  - [BanTopics](./input_scanners/ban_topics.md)
  - [Code](./input_scanners/code.md)
  - [PromptInjection](./input_scanners/prompt_injection.md)
  - [Sentiment](./input_scanners/sentiment.md)
  - [TokenLimit](./input_scanners/token_limit.md)
  - [Toxicity](./input_scanners/toxicity.md)
- Output scanners with tests:
  - [BanSubstrings](./output_scanners/ban_substrings.md)
  - [BanTopics](./output_scanners/ban_topics.md)
  - [Code](./output_scanners/code.md)
  - [Deanonymize](./output_scanners/deanonymize.md)
  - [NoRefusal](./output_scanners/no_refusal.md)
  - [Regex](./output_scanners/regex.md)
  - [Relevance](./output_scanners/relevance.md)
  - [Sensitive](./output_scanners/sensitive.md)
  - [Toxicity](./output_scanners/toxicity.md)

[Unreleased]: https://github.com/laiyer-ai/llm-guard/commits/main
[0.3.3]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.3.3
[0.3.2]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.3.2
[0.3.1]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.3.1
[0.3.0]: https://github.com/laiyer-ai/llm-guard/releases/tag/v0.3.0
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
