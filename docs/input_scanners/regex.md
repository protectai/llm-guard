# Regex Scanner

This scanner is designed to sanitize prompts based on predefined regular expression patterns.
It offers flexibility in defining patterns to identify and process desirable or undesirable content within the prompts.

## How it works

The scanner operates with a list of regular expressions, patterns. These patterns are used to identify specific formats, keywords, or phrases in the prompt.

- **Matching Logic**: The scanner evaluates the prompt against all provided patterns. If any pattern matches, the corresponding action (redaction or validation) is taken based on the `is_blocked` flag.
- **Redaction**: If enabled, the scanner will redact the portion of the prompt that matches any of the patterns.

## Usage

```python
from llm_guard.input_scanners import Regex
from llm_guard.input_scanners.regex import MatchType

# Initialize the Regex scanner
scanner = Regex(
    patterns=[r"Bearer [A-Za-z0-9-._~+/]+"],  # List of regex patterns
    is_blocked=True,  # If True, patterns are treated as 'bad'; if False, as 'good'
    match_type=MatchType.SEARCH,  # Can be SEARCH or FULL_MATCH
    redact=True,  # Enable or disable redaction
)

# Scan a prompt
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

In the above example, replace `r"Bearer [A-Za-z0-9-._~+/]+"` with your actual regex pattern.
The `is_blocked` parameter determines how the patterns are treated.
If `is_blocked` is True, any pattern match marks the prompt as invalid; if False, the prompt is considered valid if it matches any of the patterns.

## Benchmarks

Run the following script:

```sh
python benchmarks/run.py input Regex
```

This scanner uses built-in functions, which makes it fast.
