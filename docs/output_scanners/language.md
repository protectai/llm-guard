# Language Scanner

This scanner identifies and assesses the authenticity of the language used in outputs.

## Attack

With the rise of sophisticated LLMs, there has been an increase in attempts to manipulate or "confuse" these models. For example, model might produce an output in unexpected language.

The Language Scanner is designed to identify such attempts, assess the authenticity of the language used.

## How it works

At its core, the scanner leverages the capabilities of [langdetect](https://github.com/Mimino666/langdetect) library.
The primary function of the scanner is to analyze the model's output, determine its language, and check if it's in the
list.

!!! info

    Supported languages: `['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he',  'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']`.

## Usage

```python
from llm_guard.output_scanners import Language

scanner = Language(valid_languages=["en", ...])  # Add other valid languages as needed
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
