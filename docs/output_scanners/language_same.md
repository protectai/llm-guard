# LanguageSame Scanner

This scanner evaluates and checks if the prompt and output are in the same language.

## Attack scenario

There can be cases where the model produces an output in a different language than the input or prompt. This can be
unintended, especially in applications that require consistent language output.

The `LanguageSame` Scanner serves to identify these discrepancies and helps in maintaining consistent linguistic
outputs.

## How it works

At its core, the scanner leverages the capabilities of [papluca/xlm-roberta-base-language-detection](https://huggingface.co/papluca/xlm-roberta-base-language-detection) model to discern the
language of both the input prompt and the output.

It then checks whether both detected languages are the same. If they are not, it indicates a potential language
discrepancy.

It supports the 22 languages:

```text
arabic (ar), bulgarian (bg), german (de), modern greek (el), english (en), spanish (es), french (fr), hindi (hi), italian (it), japanese (ja), dutch (nl), polish (pl), portuguese (pt), russian (ru), swahili (sw), thai (th), turkish (tr), urdu (ur), vietnamese (vi), and chinese (zh)
```

!!! note

    While the scanner identifies language discrepancies, it doesn't limit or enforce any specific language sets. Instead, it simply checks for language consistency between the prompt and output. If you want to enforce languages, use Language scanner

## Usage

```python
from llm_guard.output_scanners import LanguageSame

scanner = LanguageSame()
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 14
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output LanguageSame
```

Results:

| Scanner                          | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 58.23            | 370.31                | 490.94                | 587.45                | 128.94               | 108.57  |
| AWS g5.xlarge GPU                | 39.80            | 307.85                | 407.57                | 487.35                | 108.32               | 129.25  |
| AWS g5.xlarge GPU with ONNX      | 0.12             | 22.33                 | 27.72                 | 32.04                 | 11.48                | 1219.41 |
| Azure Standard_D4as_v4           | 3.71             | 228.11                | 257.62                | 281.23                | 165.40               | 84.64   |
| Azure Standard_D4as_v4 with ONNX | 0.00             | 81.06                 | 81.56                 | 81.96                 | 79.10                | 176.98  |
