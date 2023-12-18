# Deanonymize Scanner

This scanner helps put back real values in the model's output by replacing placeholders.

When we use tools like the [Anonymize scanner](../input_scanners/anonymize.md), we replace sensitive info with placeholders. For
example, a name like "John Doe" might become `[REDACTED_PERSON_1]`. The Deanonymize scanner's job is to change these
placeholders back to the original details when needed.

## Usage

This scanner uses `Vault` object. It remembers all the changes made by
the [Anonymize scanner](../input_scanners/anonymize.md). When Deanonymize scanner sees a placeholder in the model's
output, it checks the Vault to find the original info and uses it to replace the placeholder.

First, you'll need the Vault since it keeps all the original values:

```python
from llm_guard.vault import Vault

vault = Vault()
```

Then, set up the Deanonymize scanner with the Vault:

```python
from llm_guard.output_scanners import Deanonymize

scanner = Deanonymize(vault)
sanitized_model_output, is_valid, risk_score = scanner.scan(sanitized_prompt, model_output)
```

After running the above code, `sanitized_model_output` will have the real details instead of placeholders.

## Benchmarks

It uses data structures and replace function, which makes it fast.
