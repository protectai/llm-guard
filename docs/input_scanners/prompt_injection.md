# Prompt Injection Scanner

It is specifically tailored to guard against crafty input manipulations targeting large
language models (LLM). By identifying and mitigating such attempts, it ensures the LLM operates securely without
succumbing to injection attacks.

## Attack scenario

Injection attacks, especially in the context of LLMs, can lead the model to perform unintended actions. There are two
primary ways an attacker might exploit:

- **Direct Injection**: Directly overwrites system prompts.

- **Indirect Injection**: Alters inputs coming from external sources.

As specified by the `OWASP Top 10 LLM attacks`, this vulnerability is categorized under:

[LLM01: Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - It's crucial to
monitor and validate prompts rigorously to keep the LLM safe from such threats.

**Examples:**

- https://www.jailbreakchat.com/

Prompt injection attacks are particularly potent in the following scenarios:

- **Retrieval augmented generation (RAG)**: RAG utilizes a vector database to hold a large amount of data that the LLM
  may not have seen during training. This allows the model to cite data sources, provide better-supported responses, or
  be customized for different enterprises. The adversary may prompt inject some of the documents included in the
  database, and the attack activates when the model reads those documents.
- **Chatbot with a web-browsing capability**: This scenario is similar to RAG, but instead of a local database, the
  model can access any website on the internet often via a browsing tool or an API (rather than computing a vector
  similarity like RAG). Indirect prompt injection attack is particularly potent in this case as data on the internet are
  mostly unfiltered and can be dynamically changed to hide or activate the attack at any time.
- **Automated customer service applications that read and write emails**: The application might use a LLM to summarize
  or read and respond to messages. An attacker can send a message containing an injected prompt, and thereby manipulate
  the behavior of the app in unexpected ways.

## How it works

Choose models you would like to validate against:

[ProtectAI/deberta-v3-base-prompt-injection-v2](https://huggingface.co/ProtectAI/deberta-v3-base-prompt-injection-v2).
This model is a fine-tuned version of the `microsoft/deberta-v3-base` on multiple dataset of prompt injections and
normal prompts to classify text.
It aims to identify prompt injections, classifying inputs into two categories: `0` for no injection and `1` for
injection detected. We are still testing it.

Usage:

```python
from llm_guard.input_scanners import PromptInjection
from llm_guard.input_scanners.prompt_injection import MatchType

scanner = PromptInjection(threshold=0.5, match_type=MatchType.FULL)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

!!! info

    Switching the match type might help with improving the accuracy, especially for longer prompts.

!!! warning

    We don't recommend using this scanner for system prompts. It's designed to work with user inputs.

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 384
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input PromptInjection --use-onnx=1
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                    | 3.00             | 269.14                | 295.71                | 316.97                | 212.87               | 1803.91  |
| AWS m5.xlarge with ONNX          | 0.00             | 106.65                | 106.85                | 107.01                | 104.21               | 3684.92  |
| AWS g5.xlarge GPU                | 17.00            | 211.63                | 276.70                | 328.76                | 81.01                | 4739.91  |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 11.44                 | 13.28                 | 14.75                 | 7.65                 | 50216.67 |
| AWS r6a.xlarge (AMD)             | 0.02             | 209.49                | 211.40                | 212.92                | 205.05               | 1872.73  |
| AWS r6a.xlarge (AMD) with ONNX   | 0.08             | 112.10                | 116.38                | 119.81                | 103.21               | 3720.40  |
| Azure Standard_D4as_v4           | 184.23           | 852.63                | 1066.26               | 1237.16               | 421.46               | 911.11   |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 179.81                | 180.22                | 180.55                | 177.30               | 2165.87  |
