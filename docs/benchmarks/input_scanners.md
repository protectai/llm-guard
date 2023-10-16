# Input scanners benchmarks

Reference
code: [benchmarks/scan_prompt_latency.py](https://github.com/laiyer-ai/llm-guard/blob/main/benchmarks/scan_prompt_latency.py)

## Test environment

- Platform: Amazon Linux 2
- Python Version: 3.10.2

## Setup

- Basic scanners: [Anonymize](../input_scanners/anonymize.md), [Secrets](../input_scanners/secrets.md).
- Intermediate
  scanners: [Anonymize](../input_scanners/anonymize.md), [Secrets](../input_scanners/secrets.md), [PromptInjection](../input_scanners/prompt_injection.md), [Toxicity](../input_scanners/toxicity.md).
- Advanced scanners: All scanners.

## AWS `m5.large` instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | Make an SQL insert statement...      | 19.64    | 80.91    | 32.16     | 20.17    | 27.25       |
| Basic        | For some reason, the assistant is... | 24.74    | 25.56    | 25.02     | 24.92    | 0.32        |
| Intermediate | Make an SQL insert statement...      | 1,058.04 | 1,101.77 | 1,071.13  | 1,064.81 | 17.57       |
| Intermediate | For some reason, the assistant is... | 1,124.88 | 1,128.45 | 1,126.95  | 1,127.28 | 1.30        |
| Advanced     | Make an SQL insert statement...      | 1,491.25 | 1,588.25 | 1,514.28  | 1,499.31 | 41.56       |
| Advanced     | For some reason, the assistant is... | 1,412.07 | 1,428.43 | 1,420.79  | 1,421.61 | 6.26        |

## AWS `inf1.xlarge` instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | Make an SQL insert statement...      | 18.7     | 84.96    | 33.22     | 19.31  | 29.0        |
| Basic        | For some reason, the assistant is... | 22.69    | 23.29    | 22.92     | 22.85  | 0.22        |
| Intermediate | Make an SQL insert statement...      | 548.72   | 593.03   | 561.52    | 552.01 | 18.42       |
| Intermediate | For some reason, the assistant is... | 581.89   | 604.52   | 594.88    | 596.55 | 8.18        |
| Advanced     | Make an SQL insert statement...      | 746.46   | 763.8    | 755.67    | 758.59 | 7.1         |
| Advanced     | For some reason, the assistant is... | 779.55   | 889.47   | 806.11    | 783.72 | 47.12       |

## AWS `g5.xlarge` (one GPU) instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | Make an SQL insert statement...      | 15.64    | 46.84    | 22.6      | 16.88  | 13.57       |
| Basic        | For some reason, the assistant is... | 20.39    | 21.48    | 20.81     | 20.75  | 0.33        |
| Intermediate | Make an SQL insert statement...      | 52.53    | 122.05   | 67.19     | 54.0   | 30.68       |
| Intermediate | For some reason, the assistant is... | 58.19    | 61.10    | 59.4      | 59.4   | 1.09        |
| Advanced     | Make an SQL insert statement...      | 117.01   | 162.65   | 127.58    | 119.65 | 19.63       |
| Advanced     | For some reason, the assistant is... | 144.03   | 148.36   | 146.4     | 147.42 | 1.88        |
