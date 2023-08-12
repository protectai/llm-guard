# Sensitive Scanner

The Sensitive scanner actively scans the output from the language model, ensuring no Personal Identifiable Information (
PII), secrets or sensitive data slips through.

## Attack

Sensitive Information Disclosure is a noted vulnerability in Language Learning Models (LLM). Such models may
accidentally provide responses that contain confidential data. This poses risks such as unauthorized data access,
violations of privacy, and even more severe security breaches. Addressing this is paramount, and that's where the
Sensitive Data Detector comes into play.

Referring to the `OWASP Top 10 for Large Language Model Applications`, this falls under:

[LLM06: Sensitive Information Disclosure]((https://owasp.org/www-project-top-10-for-large-language-model-applications/)) -
To combat this, it's vital to integrate data sanitization and adopt strict user policies.

## How it works

It takes advantage of the [Presidio Analyzer Engine](https://github.com/microsoft/presidio/). Coupled
with predefined internal patterns, the tool offers robust scanning capabilities.

It uses transformers based model `en_core_web_trf` which uses a more modern deep-learning architecture, but is generally
slower than the default `en_core_web_lg` model.

When running, the scanner inspects the model's output for specific entity types that may be considered sensitive. If no
types are chosen, the tool defaults to scanning for all known entity types, offering comprehensive coverage.

### Entities

_Note: Entity detection only works in English right now_

- [List of all entities](../../llm_guard/input_scanners/anonymize.py)
- [Supported Presidio entities](https://microsoft.github.io/presidio/supported_entities/#list-of-supported-entities)
- [Custom patterns](../../llm_guard/resources/sensisitive_patterns.json)

## Usage

Here's a quick example of how you can use the Sensitive Data Detector:

```python
from llm_guard.output_scanners import Sensitive

scanner = Sensitive(entity_types=["NAME", "EMAIL"])
sanitized_output, is_valid = scanner.scan(prompt, model_output)
```

If you want, you can use your own patterns by giving the path in `regex_pattern_groups_path`

In the example, we're particularly checking for names and emails. If the output_clean contains any PII, the is_clean
will be False.
