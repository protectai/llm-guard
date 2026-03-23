# MiniMax

This tutorial demonstrates how to use LLM Guard as a security firewall for [MiniMax](https://www.minimaxi.com/) LLM API calls.

MiniMax provides an OpenAI-compatible API, so integration uses the standard OpenAI Python SDK with a custom `base_url`.

## Available Models

| Model | Context Window | Description |
|-------|---------------|-------------|
| MiniMax-M2.7 | 1M tokens | Latest flagship model |
| MiniMax-M2.5 | 204K tokens | High-performance model |
| MiniMax-M2.5-highspeed | 204K tokens | Optimized for speed |

## Simple Example

In [minimax_api.py](https://github.com/protectai/llm-guard/blob/main/examples/minimax_api.py), LLM Guard is used to protect MiniMax API calls.

All scanners run sequentially before the request is sent to the MiniMax API. Then, once the response is received, it is scanned by the output scanners.

### Setup

```bash
pip install llm-guard openai
export MINIMAX_API_KEY="your-api-key"
```

### Usage

```python
import os
from openai import OpenAI
from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

client = OpenAI(
    api_key=os.getenv("MINIMAX_API_KEY"),
    base_url="https://api.minimax.io/v1",
)
vault = Vault()
input_scanners = [Anonymize(vault), Toxicity(), TokenLimit(), PromptInjection()]
output_scanners = [Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()]

prompt = "Your user prompt here"

# Scan the prompt
sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, prompt)
if any(results_valid.values()) is False:
    print(f"Prompt is not valid, scores: {results_score}")
    exit(1)

# Call MiniMax API with sanitized prompt
response = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": sanitized_prompt},
    ],
    temperature=0.1,
    max_tokens=512,
)
response_text = response.choices[0].message.content

# Scan the output
sanitized_response_text, results_valid, results_score = scan_output(
    output_scanners, sanitized_prompt, response_text
)
if not all(results_valid.values()) is True:
    print(f"Output is not valid, scores: {results_score}")
    exit(1)

print(f"Output: {sanitized_response_text}")
```

## Streaming Example

In [minimax_streaming.py](https://github.com/protectai/llm-guard/blob/main/examples/minimax_streaming.py), LLM Guard is used with MiniMax in streaming mode.

The prompt is scanned in parallel with the request to the MiniMax API. If the prompt is not safe, the request will be blocked.

Then, the response is scanned in streaming mode (in chunks). If any chunk is not safe, the response will be blocked.

## Using with LiteLLM

MiniMax can also be used via [LiteLLM](./litellm.md) proxy, which provides a unified interface across providers. Configure MiniMax in your LiteLLM config:

```yaml
model_list:
  - model_name: minimax-m2.7
    litellm_params:
      model: openai/MiniMax-M2.7
      api_key: os.environ/MINIMAX_API_KEY
      api_base: https://api.minimax.io/v1

litellm_settings:
    callbacks: ["llmguard_moderations"]
```
