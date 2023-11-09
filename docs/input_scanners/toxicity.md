# Toxicity Scanner

It provides a mechanism to analyze and gauge the toxicity of prompt, assisting in maintaining the health and safety of
online interactions by preventing the dissemination of potentially harmful content.

## Attack

Online platforms can sometimes be used as outlets for toxic, harmful, or offensive content. By identifying and
mitigating such content at the source (i.e., the user's prompt), platforms can proactively prevent the escalation of
such situations and foster a more positive and constructive environment.

## How it works

Utilizing the power of the [unitary/unbiased-toxic-roberta](https://huggingface.co/unitary/unbiased-toxic-roberta) from
Hugging Face, the scanner performs a binary classification on the provided text, assessing whether it's toxic or not.

If deemed toxic, the toxicity score reflects the model's confidence in this classification.

If identified as non-toxic, the score is the inverse of the model's confidence, i.e., 1 - confidence_score.

If the resulting toxicity score surpasses a predefined threshold, the text is flagged as toxic. Otherwise, it's
classified as non-toxic.

## Usage

```python
from llm_guard.input_scanners import Toxicity

scanner = Toxicity(threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances.

To enable it, install the `onnxruntime` package:

```sh
pip install llm-guard[onnxruntime]
```

And set the `use_onnx` parameter to `True`:

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input Toxicity
```

Results:

| Instance                | Input Length | Test Times | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS     |
|-------------------------|--------------|------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|---------|
| AWS m5.xlarge           | 97           | 5          | 2.86             | 140.00                | 166.73                | 188.11                | 86.41                | 1122.57 |
| AWS m5.xlarge with ONNX | 97           | 5          | 0.00             | 35.66                 | 36.07                 | 36.40                 | 34.59                | 2804.45 |
| AWS g5.xlarge GPU       | 97           | 5          | 29.64            | 266.58                | 352.57                | 421.36                | 94.24                | 1029.32 |
