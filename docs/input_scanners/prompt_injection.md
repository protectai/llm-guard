# Prompt Injection Scanner

It is specifically tailored to guard against crafty input manipulations targeting large
language models (LLM). By identifying and mitigating such attempts, it ensures the LLM operates securely without
succumbing to injection attacks.

## Attack scenario

Injection attacks, especially in the context of LLMs, can lead the model to perform unintended actions. There are two
primary ways an attacker might exploit:

- **Direct Injection**: Directly overwrites system prompts.

- **Indirect Injection**: Alters inputs coming from external sources.

!!! info

    As specified by the `OWASP Top 10 LLM attacks`, this vulnerability is categorized under:

    [LLM01: Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - It's crucial to
    monitor and validate prompts rigorously to keep the LLM safe from such threats.

**Examples:**

- https://www.jailbreakchat.com/

## How it works

Choose models you would like to validate against:

[laiyer/deberta-v3-base-prompt-injection](https://huggingface.co/laiyer/deberta-v3-base-prompt-injection).
This model is a fine-tuned version of the `microsoft/deberta-v3-base` on multiple dataset of prompt injections and normal prompts to classify text.
It aims to identify prompt injections, classifying inputs into two categories: `0` for no injection and `1` for injection detected. We are still testing it.

Usage:

```python
from llm_guard.input_scanners import PromptInjection
from llm_guard.input_scanners.prompt_injection import MODEL_LAIYER

scanner = PromptInjection(threshold=0.5, models=[MODEL_LAIYER])
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch
Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime] # for CPU instances
pip install llm-guard[onnxruntime-gpu] # for GPU instances
```

And set `use_onnx=True`.

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
| Azure Standard_D4as_v4           | 184.23           | 852.63                | 1066.26               | 1237.16               | 421.46               | 911.11   |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 179.81                | 180.22                | 180.55                | 177.30               | 2165.87  |
