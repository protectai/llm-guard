# Regex Scanner

This scanner is designed to sanitize outputs based on predefined regular expression patterns.
It offers flexibility in defining patterns to identify and process desirable or undesirable content within the outputs.

## How it works

The scanner operates with a list of regular expressions, patterns. These patterns are used to identify specific formats, keywords, or phrases in the output.

- **Matching Logic**: The scanner evaluates the output against all provided patterns. If any pattern matches, the corresponding action (redaction or validation) is taken based on the `is_blocked` flag.
- **Redaction**: If enabled, the scanner will redact the portion of the output that matches any of the patterns.

## Usage

```python
from llm_guard.output_scanners import Regex
from llm_guard.input_scanners.regex import MatchType

# Initialize the Regex scanner
scanner = Regex(
    patterns=[r"Bearer [A-Za-z0-9-._~+/]+"],  # List of regex patterns
    is_blocked=True,  # If True, patterns are treated as 'bad'; if False, as 'good'
    match_type=MatchType.SEARCH,  # Can be SEARCH or FULL_MATCH
    redact=True,  # Enable or disable redaction
)

# Scan an output
sanitized_output, is_valid, risk_score = scanner.scan(prompt, output)
```

In the above example, replace `r"Bearer [A-Za-z0-9-._~+/]+"` with your actual regex pattern.
The `is_blocked` parameter determines how the patterns are treated.
If `is_blocked` is True, any pattern match marks the output as invalid; if False, the output is considered valid if it matches any of the patterns.

## Benchmarks

Run the following script:

```sh
python benchmarks/run.py output Regex
```

This scanner uses built-in functions, which makes it fast.
