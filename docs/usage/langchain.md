# Langchain

[Langchain](https://github.com/langchain-ai/langchain) stands out as a leading AI framework, renowned for its unique approach to "Constructing applications using LLMs via composability."

But, while LangChain facilitates application construction, it doesn't directly handle LLM security. That's where LLMGuard comes into play. By pairing LLMGuard with LangChain, you're equipped with a comprehensive platform for creating regulated and adherence-driven applications anchored by language models.

## Installation

1. Install dependencies:

```bash
pip install llm-guard langchain openai
```

2. Configure API key:

```bash
export OPENAI_API_KEY="<your key>"
```

## Usage

[LangChain Expression Language or LCEL](https://python.langchain.com/docs/expression_language/) is a declarative way to easily compose chains together.

We can chain LLM Guard and the LLM sequentially. This means that we check if LLM Guard has identified any security risk in the prompt before it is sent to the LLM to get an output.

And then use another scanner to check if the output from the LLM is safe to be sent to the user.

In [examples/langchain.py](https://github.com/laiyer-ai/llm-guard/blob/main/examples/langchain.py), you can find an example of how to use LCEL to compose LLM Guard chains.

Additionally, there is a Jupyter Notebook available with more details: [examples/langchain.ipynb](https://github.com/laiyer-ai/llm-guard/blob/main/examples/langchain.ipynb).
