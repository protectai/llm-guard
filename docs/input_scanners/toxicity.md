# Toxicity Scanner

It provides a mechanism to analyze and gauge the toxicity of prompt, assisting in maintaining the health and safety of
online interactions by preventing the dissemination of potentially harmful content.

## Attack

Online platforms can sometimes be used as outlets for toxic, harmful, or offensive content. By identifying and
mitigating such content at the source (i.e., the user's prompt), platforms can proactively prevent the escalation of
such situations and foster a more positive and constructive environment.

## How it works

Utilizing the power of the [martin-ha/toxic-comment-model](https://huggingface.co/martin-ha/toxic-comment-model) from
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

## Limitations

While the model is trained to recognize and classify a wide range of toxic online interactions, it does have certain
shortcomings:

Some comments referring to specific identity subgroups, such as "Muslim", might not be classified accurately. This is a
known limitation and work is ongoing to improve this aspect.

## Optimizations

### ONNX

The scanner can run on ONNX Runtime, which provides a significant performance boost on CPU instances.

To enable it, install the `onnxruntime` package:

```sh
pip install onnx onnxruntime optimum[onnxruntime]
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

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.036         | 2726.15               | 97                     |
| m5.large (AWS)    | 0.061         | 1592.14               | 97                     |
