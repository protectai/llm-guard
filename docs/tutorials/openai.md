# OpenAI ChatGPT

This example demonstrates how to use LLM Guard as a firewall of OpenAI client.

## Simple example

In [openai_api.py](https://github.com/protectai/llm-guard/blob/main/examples/openai_api.py), LLM Guard is used to protect OpenAI ChatGPT client.

All scanners will run sequentially before the request is sent to the OpenAI API. Then, once the request is received, the response will be scanned by the scanners.

## Advanced example

In [openai_streaming.py](https://github.com/protectai/llm-guard/blob/main/examples/openai_streaming.py), LLM Guard is used to protect OpenAI ChatGPT client with streaming.

The prompt is scanned in parallel with the request to the OpenAI API. If the prompt is not safe, the request will be blocked.

Then, the response is scanned in a streaming mode i.e. in chunks. If any chunk is not safe, the response will be blocked.
