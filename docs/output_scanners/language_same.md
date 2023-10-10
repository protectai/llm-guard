# LanguageSame Scanner

This scanner evaluates and checks if the prompt and output are in the same language.

## Attack

There can be cases where the model produces an output in a different language than the input or prompt. This can be unintended, especially in applications that require consistent language output.

The `LanguageSame` Scanner serves to identify these discrepancies and helps in maintaining consistent linguistic outputs.

## How it works

The scanner predominantly utilizes the [langdetect](https://github.com/Mimino666/langdetect) library to discern the language of both the input prompt and the output.

!!! info

    Supported languages: `['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he',  'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']`.

It then checks whether both detected languages are the same. If they are not, it indicates a potential language discrepancy.

!!! note

    While the scanner identifies language discrepancies, it doesn't limit or enforce any specific language sets. Instead, it simply checks for language consistency between the prompt and output. If you want to enforce languages, use Language scanner

## Usage

```python
from llm_guard.output_scanners import LanguageSame

scanner = LanguageSame()
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
