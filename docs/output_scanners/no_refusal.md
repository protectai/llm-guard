# No Refusal Scanner

It is specifically designed to detect refusals in the output of language models.

By using zero-shot classification, it can
ascertain whether the model has produced a refusal in response to a
potentially harmful or policy-breaching prompt.

## Attack scenario

Refusals are responses produced by language models when confronted with prompts that are considered to be against the
policies set by the model. Such refusals are important safety mechanisms, guarding against misuse of the model. Examples
of refusals can include statements like "Sorry, I can't assist with that" or "I'm unable to provide that information."

## How it works

It leverages the power
of HuggingFace
model [MoritzLaurer/deberta-v3-large-zeroshot-v1](https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v1)
to classify the model's output.

## Usage

```python
from llm_guard.output_scanners import NoRefusal

scanner = NoRefusal(threshold=0.5)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch
Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 47
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output NoRefusal
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 2.86             | 1048.77               | 1075.02               | 1096.03               | 994.49               | 47.26   |
| AWS m5.xlarge with ONNX          | 0.10             | 258.20                | 262.98                | 266.80                | 247.92               | 189.57  |
| AWS g5.xlarge GPU                | 28.92            | 319.38                | 404.24                | 472.13                | 149.02               | 315.40  |
| AWS g5.xlarge GPU with ONNX      | 0.13             | 37.97                 | 43.70                 | 48.28                 | 26.42                | 1778.77 |
| Azure Standard_D4as_v4           | 4.12             | 1136.88               | 1167.30               | 1191.64               | 1069.95              | 43.93   |
| Azure Standard_D4as_v4 with ONNX | 4.13             | 379.90                | 402.37                | 420.35                | 303.08               | 155.08  |
