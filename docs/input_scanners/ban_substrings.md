# Ban Substrings Scanner

Ensure that specific undesired substrings never make it into your prompts with the BanSubstrings scanner.

## How it works

It is purpose-built to screen user prompts, ensuring none of the banned substrings are present.
Users have the flexibility to enforce this check at two distinct granularity levels:

- **String Level**: The banned substring is sought throughout the entire user prompt.

- **Word Level**: The scanner exclusively hunts for whole words that match the banned substrings, ensuring no individual
  standalone words from the blacklist appear in the prompt.

Additionally, the scanner can be configured to replace the banned substrings with `[REDACT]` in the model's output.

## Usage

```python
from llm_guard.input_scanners import BanSubstrings

scanner = BanSubstrings(substrings=["forbidden", "unwanted"], match_type="word", case_sensitive=False, redact=False,
                        contains_all=False)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

In the above configuration, `is_valid` will be `False` if the provided `prompt` contains any of the banned substrings as
whole words. To ban substrings irrespective of their word boundaries, simply change the mode to `str`.

There is also a dataset prepared of harmful substrings for
prompts: [prompt_stop_substrings.json](https://github.com/laiyer-ai/llm-guard/blob/main/llm_guard/resources/prompt_stop_substrings.json)

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input BanSubstrings
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.0           | 243606.68             | 45                     |
| m5.large (AWS)    | 0.0           | 216970.99             | 45                     |

!!! info:

    This scanner uses built-in functions, which makes it fast.
