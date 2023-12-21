# Retrieval-augmented Generation (RAG)

## What is RAG?

RAG (Retrieval Augmented Generation) is a technique for augmenting LLM knowledge with additional, often private or real-time, data.

LLMs can reason about wide-ranging topics, but their knowledge is limited to the public data up to a specific point in time that they were trained on.
If you want to build AI applications that can reason about private data or data introduced after a model’s cutoff date, you need to augment the knowledge of the model with the specific information it needs. The process of bringing the appropriate information and inserting it into the model prompt is known as Retrieval Augmented Generation (RAG).

## Why RAG should be secure?

During retrieval stage, we need to add context to the prompt with relevant documents. However, the documents may contain sensitive information, hidden prompt injection or other malicious content. Therefore, we need to secure the retrieval stage to prevent the model from being poisoned.
