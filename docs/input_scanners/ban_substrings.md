# Ban Substrings Scanner

Ensure that specific undesired substrings never make it into your prompts with the BanSubstrings scanner.

## How it works

It is purpose-built to screen user prompts, ensuring none of the banned substrings are present.
Users have the flexibility to enforce this check at two distinct granularity levels:

- **String Level**: The banned substring is sought throughout the entire user prompt.

- **Word Level**: The scanner exclusively hunts for whole words that match the banned substrings, ensuring no individual
  standalone words from the blacklist appear in the prompt.

## Usage

```python
from llm_guard.input_scanners import BanSubstrings

scanner = BanSubstrings(substrings=["forbidden", "unwanted"], match_type="word", case_sensitive=False)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

In the above configuration, `is_valid` will be `False` if the provided `prompt` contains any of the banned substrings as
whole words. To ban substrings irrespective of their word boundaries, simply change the mode to `str`.

There is also a dataset prepared of harmful substrings for
prompts: [prompt_stop_substrings.json](https://github.com/laiyer-ai/llm-guard/blob/main/llm_guard/resources/prompt_stop_substrings.json)
