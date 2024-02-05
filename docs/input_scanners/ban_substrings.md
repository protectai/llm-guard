# Ban Substrings Scanner

Ensure that specific undesired substrings never make it into your prompts with the BanSubstrings scanner.

## How it works

It is purpose-built to screen user prompts, ensuring none of the banned substrings are present.
Users have the flexibility to enforce this check at two distinct granularity levels:

- **String Level**: The banned substring is sought throughout the entire user prompt.

- **Word Level**: The scanner exclusively hunts for whole words that match the banned substrings, ensuring no individual
  standalone words from the blacklist appear in the prompt.

Additionally, the scanner can be configured to replace the banned substrings with `[REDACT]` in the model's output.

## Use cases

1. Check that competitors' names are not present in the prompt.

2. Prevent harmful substrings for prompts: [prompt_stop_substrings.json](https://github.com/protectai/llm-guard/blob/main/llm_guard/resources/prompt_stop_substrings.json).

3. Hide predefined list of URLs you don't want to be mentioned in the prompt.

## Usage

```python
from llm_guard.input_scanners import BanSubstrings
from llm_guard.input_scanners.ban_substrings import MatchType

competitors_names = [
    "Acorns",
    "Citigroup",
    "Citi",
    "Fidelity Investments",
    "Fidelity",
    "JP Morgan Chase and company",
    "JP Morgan",
    "JP Morgan Chase",
    "JPMorgan Chase",
    "Chase" "M1 Finance",
    "Stash Financial Incorporated",
    "Stash",
    "Tastytrade Incorporated",
    "Tastytrade",
    "ZacksTrade",
    "Zacks Trade",
]

scanner = BanSubstrings(
  substrings=competitors_names,
  match_type=MatchType.STR,
  case_sensitive=False,
  redact=False,
  contains_all=False,
)

sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

In the above configuration, `is_valid` will be `False` if the provided `prompt` contains any of the banned substrings as
whole words. To ban substrings irrespective of their word boundaries, simply change the mode to `str`.

## Benchmarks

Run the following script:

```sh
python benchmarks/run.py input BanSubstrings
```

This scanner uses built-in functions, which makes it fast.
