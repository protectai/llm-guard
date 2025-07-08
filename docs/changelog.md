# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 0.3.17

### Added
-

### Fixed
-

### Changed
-

### Removed
-

## [0.3.16] - 2025-05-19

### Fixed
- Regex scanner redacts only the first occurrence ([#229](https://github.com/protectai/llm-guard/issues/229)).
- BanSubstrings scanner redacts only the first occurrence ([#210](https://github.com/protectai/llm-guard/issues/210)).

### Changed
- Upgrade all dependencies.
- Stop substrings moved to the variables instead of JSON files.
- **[BREAKING]** New logic to calculate the risk score ([#182](https://github.com/protectai/llm-guard/issues/182)).

## [0.3.15] - 2024-08-22

### Changed
- Upgrade dependencies to the latest versions.
- `Bias` scanner uses the prompt to increase the accuracy.

## [0.3.14] - 2024-06-17

### Added
- In API, suppress specific scanners when running the analysis.

### Changed
- Allow custom `uvicorn` configuration in the API deployment.
- Add support of Python v3.12
- In API, removed `gunicorn` support as `uvicorn` [supports workers](https://fastapiexpert.com/blog/2024/05/28/uvicorn-0300-release/).

### Removed
- Caching is removed from the API deployment as it was causing issues when running multiple workers.
- `use_io_binding` parameter is removed for the ONNX inference to allow the client to control it.

## [0.3.13] - 2024-05-10

### Fixed
- `BanSubstrings` scanner to handle substrings with special characters.

### Changed
- `Gibberish` scanner has higher threshold to reduce false positives. In addition, it supports changing `labels` to remove overtriggering when `mild gibberish` is detected.
- `BanCode` scanner was improved to trigger less false-positives.
- Improved logging to support JSON format both in the library and `API`.
- Optimizations in the `API` to reduce the latency.
- `BanCompetitors` scanner relies on the new model which also supports ONNX inference.

## [0.3.12] - 2024-04-23

### Added
- Lazy loading of models in the API deployment. Now you can start loading models when the first request comes.
- Support for `gunicorn` in the API deployment.
- `NoRefusalLight` scanner that uses a common set of phrases to detect refusal as per research papers.
- `Anonymize` and `Sensitive` scanners have a support of [lakshyakh93/deberta_finetuned_pii](https://huggingface.co/lakshyakh93/deberta_finetuned_pii) model.
- `BanCode` scanner to detect and block code snippets in the prompt.
- Benchmarks on the AMD CPU.
- `API` has a new endpoint `POST /scan/prompt` to scan the prompt without sanitizing it. It is faster than the `POST /analyze/scan` endpoint.
- Example of running [LLM Guard with ChatGPT streaming mode](./tutorials/openai.md) enabled.
- `API` supports loading models from the local folder.

### Fixed
- `InvisibleText` scanner to allow control characters like `\n`, `\t`, etc.

### Changed
- **[Breaking]**: Introducing `Model` object for better customization of the models.
- Updated all libraries
- Introduced `revision` for all models to ensure the same model is used for the same revision.
- `Code` scanner to rely on the output if there is no Code in the prompt.
- `BanTopics`, `FactualConsistency`: support of the [new zero-shot-classification models](https://huggingface.co/collections/MoritzLaurer/zeroshot-classifiers-6548b4ff407bb19ff5c3ad6f).
- `PromptInjection` can support more match types for better accuracy.
- `API` relies on the lighter models for faster inference but with a bit lower accuracy. You can remove the change and build from source to use the full models.
- `PromptInjection` scanned uses the [new v2 model](https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2) for better accuracy.

### Removed
- `model_kwargs` and `pipeline_kwargs` as they are part of the `Model` object.

## [0.3.10] - 2024-03-14

### Added
- **Anonymize**: New NER models from AI4Privacy [Isotonic/distilbert_finetuned_ai4privacy_v2](https://huggingface.co/Isotonic/distilbert_finetuned_ai4privacy_v2) and [Isotonic/deberta-v3-base_finetuned_ai4privacy_v2](https://huggingface.co/Isotonic/deberta-v3-base_finetuned_ai4privacy_v2).
- [Gibberish](./input_scanners/gibberish.md) scanner to check if the text contains gibberish.
- Ability to load models from local folders instead of pulling them from HuggingFace.

### Fixed
-

### Changed
- API Documentation and Code improvements.
- Improved logging to expose more information.
- **Anonymize**: Tweaks for pattern-based matching.
- Pass `pipeline` and `model` `kwargs` for better control over the models.
- Relax validations to accept custom models.
- **[Breaking]**: `Anonymize` scanner patterns are configured in Python instead of JSON file.

### Removed
-

## [0.3.9] - 2024-02-08

**[Laiyer is now part of Protect AI](https://protectai.com/press/protect-ai-acquires-laiyer-ai)**

### Added
- `Anonymize`: language support with `zh` ([#79](https://github.com/protectai/llm-guard/pull/79), thanks to [@Oscaner](https://github.com/Oscaner)).
- `Anonymize`: more regex patterns, such as `PO_BOX_RE`, `PRICE_RE`, `HEX_COLOR`, `TIME_RE`, `DATE_RE`, `URL_RE`, `PHONE_NUMBER_WITH_EXT`, `BTC_ADDRESS`
- Add [NIST Taxonomy](./get_started/attacks.md) to the documentation.
- Pass HuggingFace Transformers `pipeline` `kwargs` for better control over the models. For example, `BanTopics(topics=["politics", "war", "religion"], transformers_kwargs={"low_cpu_mem_usage": True})` for better memory usage when handling big models.
- `API`: rate limiting.
- `API`: HTTP basic authentication and API key authentication.
- `API`: OpenTelemetry support for tracing and metrics.

### Fixed
- Incorrect results when using `Deanonymize` multiple times ([#82](https://github.com/protectai/llm-guard/pull/82), thanks to [@andreaponti5](https://github.com/andreaponti5))

### Changed
- `NoRefusal` scanner relies on the proprietary model [ProtectAI/distilroberta-base-rejection-v1](https://huggingface.co/ProtectAI/distilroberta-base-rejection-v1).
- `NoRefusal` support `match_type` parameter to choose between `sentence` and `all` matches.
- Using `structlog` for better logging.
- **[Breaking]**: `Code`: using new model [philomath-1209/programming-language-identification](https://huggingface.co/philomath-1209/programming-language-identification) with more languages support and better accuracy. Please update your `languages` parameter.
- `API`: ONNX is enabled by default.
- `protobuf` version is not capped to v3.
- `API` uses `pyproject.toml` for dependencies and builds.
- **[Breaking]**: `API` configuration changes with separate sections for `auth`, `rate_limit` and `cache`.

### Removed
- Roadmap documentation as it's not up-to-date.

## [0.3.7] - 2023-01-15

_0.3.5 and 0.3.6 were skipped due to build issues._

### Added
- [URLReachability](./output_scanners/url_reachability.md) scanner to check if the URL is reachable.
- [BanCompetitors](./input_scanners/ban_competitors.md) scanner to check if the prompt or output contains competitors' names.
- [InvisibleText](./input_scanners/invisible_text.md) scanner to check if the prompt contains invisible unicode characters (steganography attack).
- [ReadingTime](./output_scanners/reading_time.md) scanner to check if the output can be read in less than a certain amount of time.
- Example of [invisible prompt attack](tutorials/attacks/invisible_prompt.ipynb) using `InvisibleText` scanner.
- Example of [making Langchain agents secure](./tutorials/notebooks/langchain_agents.ipynb).

### Fixed
- `BanSubstrings`: bug when `case_sensitive` was enabled.
- `Bias` calculation of risk score based on the threshold.

### Changed
- Using `pyproject.toml` instead of `setup.py` based on the [request](https://github.com/protectai/llm-guard/issues/68).
- **[Breaking]** `Regex` scanners have a new signature. It accepts `patterns`, `is_blocked` and `match_type`.
- **[Breaking]** `BanSubstrings`: `match_type` parameter became `Enum` instead of `str`.
- **[Breaking]** `Code` scanners have a new signature. It accepts `languages` and `is_blocked` instead of 2 separate lists.
- `Toxicity`, `PromptInjection`, `Bias` and `Language` scanners support sentence match for better accuracy (will become slower).
- `BanTopics`, `FactualConsistency` and `NoRefusal`: Updated zero-shot classification model to [hMoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33) with different size options.
- **[Breaking]**: Using keyword arguments for better readability of the code e.g. `scanner = BanSubstrings(["a", "b", "c"], "str", False, True, False)` would raise an error.
- **[Breaking]**: API config supports configuring same scanner multiple times with different inputs.

## [0.3.4] - 2023-12-21

### Added
- Example of [securing RAG with Langchain](./tutorials/notebooks/langchain_rag.ipynb)
- Example of [securing RAG with LlamaIndex](./tutorials/notebooks/llama_index_rag.ipynb)

### Changed
- Upgraded all libraries to the latest versions
- Improvements to the documentation
- `Deanonymize` scanner supports matching strategies
- Support of ONNX runtime on GPU for even faster inference (with massive latency improvements) and updated benchmarks

### Removed
- Usage of `dbmdz/bert-large-cased-finetuned-conll03-english` in the `Anonymize` scanner

## [0.3.3] - 2023-11-25

### Added
- Benchmarks on Azure instances

### Changed
- Upgraded `json_repair` library ([issue](https://github.com/protectai/llm-guard/issues/44))
- Use proprietary prompt injection detection model [ProtectAI/deberta-v3-base-prompt-injection](https://huggingface.co/ProtectAI/deberta-v3-base-prompt-injection)

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
- Langchain [example](https://github.com/protectai/llm-guard/blob/main/examples/langchain_lcel.py) using [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/)
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
- Added Swagger documentation on the [API](./api/overview.md) documentation page
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
- Example of API with Docker in [llm_guard_api](https://github.com/protectai/llm-guard/tree/main/llm_guard_api)
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

[Unreleased]: https://github.com/protectai/llm-guard/commits/main
[0.3.16]: https://github.com/protectai/llm-guard/releases/tag/v0.3.16
[0.3.15]: https://github.com/protectai/llm-guard/releases/tag/v0.3.15
[0.3.14]: https://github.com/protectai/llm-guard/releases/tag/v0.3.14
[0.3.13]: https://github.com/protectai/llm-guard/releases/tag/v0.3.13
[0.3.12]: https://github.com/protectai/llm-guard/releases/tag/v0.3.12
[0.3.10]: https://github.com/protectai/llm-guard/releases/tag/v0.3.10
[0.3.9]: https://github.com/protectai/llm-guard/releases/tag/v0.3.9
[0.3.7]: https://github.com/protectai/llm-guard/releases/tag/v0.3.7
[0.3.4]: https://github.com/protectai/llm-guard/releases/tag/v0.3.4
[0.3.3]: https://github.com/protectai/llm-guard/releases/tag/v0.3.3
[0.3.2]: https://github.com/protectai/llm-guard/releases/tag/v0.3.2
[0.3.1]: https://github.com/protectai/llm-guard/releases/tag/v0.3.1
[0.3.0]: https://github.com/protectai/llm-guard/releases/tag/v0.3.0
[0.2.4]: https://github.com/protectai/llm-guard/releases/tag/v0.2.4
[0.2.3]: https://github.com/protectai/llm-guard/releases/tag/v0.2.3
[0.2.2]: https://github.com/protectai/llm-guard/releases/tag/v0.2.2
[0.2.1]: https://github.com/protectai/llm-guard/releases/tag/v0.2.1
[0.2.0]: https://github.com/protectai/llm-guard/releases/tag/v0.2.0
[0.1.3]: https://github.com/protectai/llm-guard/releases/tag/v0.1.3
[0.1.2]: https://github.com/protectai/llm-guard/releases/tag/v0.1.2
[0.1.1]: https://github.com/protectai/llm-guard/releases/tag/v0.1.1
[0.1.0]: https://github.com/protectai/llm-guard/releases/tag/v0.1.0
[0.0.3]: https://github.com/protectai/llm-guard/releases/tag/v0.0.3
[0.0.2]: https://github.com/protectai/llm-guard/releases/tag/v0.0.2
[0.0.1]: https://github.com/protectai/llm-guard/releases/tag/v0.0.1
