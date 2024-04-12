# Toxicity Scanner

The Toxicity Scanner provides a mechanism to analyze and mitigate the toxicity of text content, playing a crucial role in maintaining the health and safety of online interactions.
This tool is instrumental in preventing the dissemination of harmful or offensive content.

## Attack scenario

Online platforms can sometimes be used as outlets for toxic, harmful, or offensive content. By identifying and
mitigating such content at the source (i.e., the user's prompt), platforms can proactively prevent the escalation of
such situations and foster a more positive and constructive environment.

## How it works

The scanner uses the [unitary/unbiased-toxic-roberta](https://huggingface.co/unitary/unbiased-toxic-roberta) model from Hugging Face for binary classification of the text as toxic or non-toxic.

- **Toxicity Detection**: If the text is classified as toxic, the toxicity score corresponds to the model's confidence in this classification.
- **Non-Toxicity Confidence**: For non-toxic text, the score is the inverse of the model's confidence, i.e., `1 − confidence score`.
- **Threshold-Based Flagging**: Text is flagged as toxic if the toxicity score exceeds a predefined threshold (default: 0.5).

## Usage

```python
from llm_guard.input_scanners import Toxicity
from llm_guard.input_scanners.toxicity import MatchType

scanner = Toxicity(threshold=0.5, match_type=MatchType.SENTENCE)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

**Match Types:**

- **Sentence Type**: In this mode (`MatchType.SENTENCE`), the scanner scans each sentence to check for toxic.
- **Full Text Type**: In `MatchType.FULL` mode, the entire text is scanned.

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 97
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input Toxicity
```

Results:

| Instance                         | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS      |
|----------------------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|----------|
| AWS m5.xlarge                    | 2.86             | 140.00                | 166.73                | 188.11                | 86.41                | 1122.57  |
| AWS m5.xlarge with ONNX          | 0.00             | 35.02                 | 35.40                 | 35.71                 | 34.13                | 2842.49  |
| AWS g5.xlarge GPU                | 29.64            | 266.58                | 352.57                | 421.36                | 94.24                | 1029.32  |
| AWS g5.xlarge GPU with ONNX      | 0.01             | 7.90                  | 9.43                  | 10.65                 | 4.80                 | 20221.31 |
| Azure Standard_D4as_v4           | 4.45             | 164.63                | 197.82                | 224.38                | 97.62                | 993.66   |
| Azure Standard_D4as_v4 with ONNX | 0.01             | 44.35                 | 44.39                 | 44.42                 | 40.27                | 2408.71  |
| AWS r6a.xlarge (AMD)             | 0.13             | 633.35                | 637.95                | 641.63                | 620.79               | 156.25   |
| AWS r6a.xlarge (AMD) with ONNX   | 0.06             | 525.96                | 529.62                | 532.55                | 517.73               | 187.36   |
