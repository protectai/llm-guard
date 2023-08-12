# Anonymize Scanner

It meticulously inspects user prompts, ensuring that they are free of any sensitive information
before being processed by the language model.

## Attack

Sometimes, Language Learning Models (or LLMs) can accidentally share private info from the prompts they get. This can be
bad because it might let others see or use this info in the wrong way.

To stop this from happening, we use the Anonymize scanner. It makes sure user prompts don’t have any private details
before the model sees them.

## Usage

When you use the Anonymize scanner, you can talk to LLMs without worrying about accidentally sharing private info.

The scanner uses a tool called the [Presidio Analyzer](https://github.com/microsoft/presidio/) library. This tool, built
with Python's spaCy, is really good at finding private info in text.

It uses transformers based model `en_core_web_trf` which uses a more modern deep-learning architecture, but is generally
slower than the default `en_core_web_lg` model.

On top of that, the Anonymize scanner can also understand special patterns to catch anything the Presidio Analyzer might
miss.

### Entities

_Note: Entity detection only works in English right now_

- [List of all entities](../../llm_guard/input_scanners/anonymize.py)
- [Supported Presidio entities](https://microsoft.github.io/presidio/supported_entities/#list-of-supported-entities)
- [Custom patterns](../../llm_guard/resources/sensisitive_patterns.json)

### Configuring

First, set up the Vault. It keeps a record of the info we change:

```python
from llm_guard.vault import Vault

vault = Vault()
```

Then, set up the Anonymize scanner with some options:

```python
from llm_guard.input_scanners import Anonymize, sensitive_patterns_path

scanner = Anonymize(vault, preamble="Insert before prompt", allowed_names=["John Doe"], hidden_names=["Test LLC"])
sanitized_prompt, is_valid = scanner.scan(prompt)
```

Here's what those options do:

- `preamble` tells the LLM to ignore certain things.
- `hidden_names` are names we change to something like `[REDACTED_CUSTOM_1]`.
- You can also choose specific types of info to hide using `entity_types`.
- If you want, you can use your own patterns by giving the path in `regex_pattern_groups_path`.
- `use_faker` will replace applicable entities with fake ones.

If you want to see the original info again, you can use the [Deanonymizer](../output_scanners/deanonymize.md).
