# Language Scanner

This scanner identifies and assesses the authenticity of the language used in prompts.

## Attack scenario

With the rise of sophisticated LLMs, there has been an increase in attempts to manipulate or "confuse" these models.
Some common tactics employed by users to attack LLMs include:

- **Jailbreaks and Prompt Injections in different languages**. For example, by utilizing unique aspects of the Japanese
  language to try and confuse the model. Paper: [Multilingual Jailbreak Challenges in Large Language Models](https://arxiv.org/abs/2310.06474)
- **Encapsulation & Overloading**: Using excessive code or surrounding prompts with a plethora of special characters to
  overload or trick the model.

The Language Scanner is designed to identify such attempts, assess the authenticity of the language used.

## How it works

At its core, the scanner leverages the capabilities of [papluca/xlm-roberta-base-language-detection](https://huggingface.co/papluca/xlm-roberta-base-language-detection) model.
The primary function of the scanner is to analyze the input prompt, determine its language, and check if it's in the
list.

It supports the 22 languages:

```text
arabic (ar), bulgarian (bg), german (de), modern greek (el), english (en), spanish (es), french (fr), hindi (hi), italian (it), japanese (ja), dutch (nl), polish (pl), portuguese (pt), russian (ru), swahili (sw), thai (th), turkish (tr), urdu (ur), vietnamese (vi), and chinese (zh)
```

## Usage

```python
from llm_guard.input_scanners import Language

scanner = Language(valid_languages=["en"])  # Add other valid language codes (ISO 639-1) as needed
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
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

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 1362
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py input Language
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS       |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|-----------|
| AWS m5.xlarge                    | 181.05           | 669.05                | 881.74                | 1051.90               | 243.45               | 5594.68   |
| AWS g5.xlarge GPU                | 230.33           | 750.71                | 990.65                | 1182.61               | 270.74               | 5030.57   |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 11.24                 | 12.94                 | 14.30                 | 7.79                 | 174817.81 |
| Azure Standard_D4as_v4           | 4.45             | 406.71                | 439.73                | 466.15                | 339.31               | 4014.05   |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 288.10                | 289.15                | 289.99                | 285.00               | 4778.90   |
