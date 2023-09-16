# Langchain

This example demonstrates how to integrate LLM Guard with [Langchain](https://github.com/langchain-ai/langchain), in
case your application uses it for orchestration.

## Running locally

1. Configure API key:

```bash
export OPENAI_API_KEY="<your key>"
```

2. Run [langchain.py](https://github.com/laiyer-ai/llm-guard/blob/main/examples/langchain.py)

```bash
python examples/langchain.py
```

## Usage

In [langchain.py](https://github.com/laiyer-ai/llm-guard/blob/main/examples/langchain.py), you can find
custom `LLMGuard` chain, which can be used instead of common `LLMChain`.
