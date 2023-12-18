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

## Usage

```python
from llm_guard.output_scanners import Language

scanner = Language(valid_languages=["en", ...])  # Add other valid language codes (ISO 639-1) as needed
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Optimization

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances. It will fetch
Laiyer's ONNX converted models from [Hugging Face Hub](https://huggingface.co/laiyer).

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set `use_onnx=True`.

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output Language
```

Results:

| Instance                         | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge                    | 14           | 5          | 5.27             | 112.01                | 148.29                | 177.32                | 39.36                | 355.65 |
| AWS g5.xlarge GPU                | 14           | 5          | 3.09             | 86.59                 | 114.36                | 136.57                | 30.98                | 451.90 |
| Azure Standard_D4as_v4           | 14           | 5          | 3.87             | 150.45                | 181.07                | 205.57                | 87.28                | 160.40 |
| Azure Standard_D4as_v4 with ONNX | 14           | 5          | 0.05             | 34.95                 | 38.16                 | 40.73                 | 27.65                | 506.41 |
