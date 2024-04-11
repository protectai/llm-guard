# Language Scanner

This scanner identifies and assesses the authenticity of the language used in outputs.

## Attack scenario

With the rise of sophisticated LLMs, there has been an increase in attempts to manipulate or "confuse" these models. For
example, model might produce an output in unexpected language.

The Language Scanner is designed to identify such attempts, assess the authenticity of the language used.

## How it works

At its core, the scanner leverages the capabilities of [papluca/xlm-roberta-base-language-detection](https://huggingface.co/papluca/xlm-roberta-base-language-detection) model.
The primary function of the scanner is to analyze the model's output, determine its language, and check if it's in the
list.

It supports the 22 languages:

```text
arabic (ar), bulgarian (bg), german (de), modern greek (el), english (en), spanish (es), french (fr), hindi (hi), italian (it), japanese (ja), dutch (nl), polish (pl), portuguese (pt), russian (ru), swahili (sw), thai (th), turkish (tr), urdu (ur), vietnamese (vi), and chinese (zh)
```

!!! note

    If there are no languages detected above the threshold, the scanner will return `is_valid=True` and `risk_score=0`.

## Usage

```python
from llm_guard.output_scanners import Language
from llm_guard.input_scanners.language import MatchType

scanner = Language(valid_languages=["en", ...], match_type=MatchType.FULL)  # Add other valid language codes (ISO 639-1) as needed
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
python benchmarks/run.py output Language
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge                    | 5.27             | 112.01                | 148.29                | 177.32                | 39.36                | 355.65  |
| AWS g5.xlarge GPU                | 3.09             | 86.59                 | 114.36                | 136.57                | 30.98                | 451.90  |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 7.66                  | 9.17                  | 10.38                 | 4.59                 | 3048.43 |
| Azure Standard_D4as_v4           | 3.87             | 150.45                | 181.07                | 205.57                | 87.28                | 160.40  |
| Azure Standard_D4as_v4 with ONNX | 0.05             | 34.95                 | 38.16                 | 40.73                 | 27.65                | 506.41  |
