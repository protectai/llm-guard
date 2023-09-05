# Output scanners benchmarks

!!! info

    Reference code: https://github.com/laiyer-ai/llm-guard/blob/main/benchmarks/scan_output_latency.py

## Test environment

- Platform: Linux
- Python Version: 3.10.2

## Setup

- Basic scanners: [Deanonymize](../output_scanners/deanonymize.md), [Secrets](../output_scanners/sensitive.md).
- Intermediate
  scanners: [Deanonymize](../output_scanners/deanonymize.md), [Secrets](../output_scanners/sensitive.md), [Bias](../output_scanners/bias.md), [Toxicity](../output_scanners/toxicity.md).
- Advanced scanners: All scanners.

## Instance type: AWS `m6g.large` (Graviton)

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 338.90   | 370.01   | 345.97    | 339.742  | 13.47       |
| Intermediate | INSERT INTO users (Name, Email... | 1,221.92 | 1,227    | 1,224.71  | 1,225.43 | 2.03        |
| Advanced     | INSERT INTO users (Name, Email... | 4,037.6  | 4,170.9  | 4,074.3   | 4,056.4  | 5.49        |

## AWS `m5.large` instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median  | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|---------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 206.15   | 256.63   | 216.35    | 206.25  | 22.51       |
| Intermediate | INSERT INTO users (Name, Email... | 734.10   | 745.58   | 740.73    | 740.84  | 4.58        |
| Advanced     | INSERT INTO users (Name, Email... | 2,331.6  | 2,500.7  | 2,373.0   | 2,338.7 | 7.2         |

## AWS `` (GPU) instance

TBD
