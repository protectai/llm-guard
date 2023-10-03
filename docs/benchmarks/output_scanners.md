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

## AWS `inf1.xlarge` instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 107.29   | 156.32   | 117.88    | 108.43 | 21.5        |
| Intermediate | INSERT INTO users (Name, Email... | 388.51   | 397.73   | 392.32    | 391.63 | 3.44        |
| Advanced     | INSERT INTO users (Name, Email... | 816.51   | 913.67   | 837.71    | 819.98 | 42.49       |

## AWS `g5.xlarge` (one GPU) instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 164.34   | 181.26   | 167.95    | 164.59 | 7.44        |
| Intermediate | INSERT INTO users (Name, Email... | 180.81   | 226.96   | 190.12    | 180.93 | 20.59       |
| Advanced     | INSERT INTO users (Name, Email... | 247.23   | 253.97   | 248.65    | 247.34 | 2.97        |
