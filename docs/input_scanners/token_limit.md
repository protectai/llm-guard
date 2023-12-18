# Token Limit Scanner

It ensures that prompts do not exceed a predetermined token count, helping prevent resource-intensive operations and
potential denial of service attacks on large language models (LLMs).

## Attack scenario

The complexity and size of LLMs make them susceptible to heavy resource usage, especially when processing lengthy
prompts. Malicious users can exploit this by feeding extraordinarily long inputs, aiming to disrupt service or incur
excessive computational costs.

This vulnerability is highlighted in the OWASP: [LLM04: Model Denial of Service](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## How it works

The scanner works by calculating the number of tokens in the provided prompt
using [tiktoken](https://github.com/openai/tiktoken) library. If the token count exceeds the configured limit, the
prompt is flagged as being too long.

One token usually equates to approximately 4 characters in common English text.
Roughly speaking, 100 tokens are equivalent to about 75 words.

For an in-depth understanding, refer to:

- [OpenAI Tokenizer Guide](https://platform.openai.com/tokenizer)
- [OpenAI Cookbook on Token Counting](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)

## Usage

```python
from llm_guard.input_scanners import TokenLimit

scanner = TokenLimit(limit=4096, encoding_name="cl100k_base")
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

!!! note

    Models supported for encoding `cl100k_base`: `gpt-4`, `gpt-3.5-turbo`, `text-embedding-ada-002`.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input TokenLimit
```

Results:

| Instance               | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS        |
|------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|------------|
| AWS m5.xlarge          | 282          | 5          | 0.00             | 0.69                  | 0.86                  | 1.01                  | 0.31                 | 914308.54  |
| AWS g5.xlarge GPU      | 282          | 5          | 0.00             | 0.60                  | 0.76                  | 0.89                  | 0.27                 | 1039014.63 |
| Azure Standard_D4as_v4 | 282          | 5          | 0.00             | 0.98                  | 1.26                  | 1.48                  | 0.41                 | 683912.25  |
