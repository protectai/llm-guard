# Input scanners benchmarks

Reference code: [benchmarks/scan_prompt_latency.py](https://github.com/laiyer-ai/llm-guard/blob/main/benchmarks/scan_prompt_latency.py)

## Test environment

- Platform: Amazon Linux 2
- Python Version: 3.10.2

## Setup

- Basic scanners: [Anonymize](../input_scanners/anonymize.md), [Secrets](../input_scanners/secrets.md).
- Intermediate
  scanners: [Anonymize](../input_scanners/anonymize.md), [Secrets](../input_scanners/secrets.md), [PromptInjection](../input_scanners/prompt_injection.md), [Toxicity](../input_scanners/toxicity.md).
- Advanced scanners: All scanners.

## Instance type: AWS `m6g.large` (Graviton)

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | Make an SQL insert statement...      | 360.56   | 404.38   | 369.66    | 361.09   | 19.41       |
| Basic        | For some reason, the assistant is... | 517.72   | 521.56   | 519.09    | 518.67   | 1.52        |
| Intermediate | Make an SQL insert statement...      | 1,221.92 | 1,227    | 1,224.71  | 1,225.43 | 2.03        |
| Intermediate | For some reason, the assistant is... | 1,549.82 | 2,325.64 | 1,929.78  | 1,919.46 | 306.18      |
| Advanced     | Make an SQL insert statement...      | 2,167.89 | 2,180.68 | 2,172.99  | 2,172.05 | 5.07        |
| Advanced     | For some reason, the assistant is... | 2,662.04 | 2,879.55 | 2,764.91  | 2,757.08 | 86.88       |

## AWS `m5.large` instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | Make an SQL insert statement...      | 211.75   | 252.38   | 220.28    | 212.71   | 17.94       |
| Basic        | For some reason, the assistant is... | 317.44   | 323.65   | 320.08    | 318.84   | 2.92        |
| Intermediate | Make an SQL insert statement...      | 620.28   | 632.61   | 627.26    | 629.0    | 4.8         |
| Intermediate | For some reason, the assistant is... | 782.69   | 1,101.70 | 937.67    | 924.63   | 127.35      |
| Advanced     | Make an SQL insert statement...      | 1,145.41 | 1,184.17 | 1,160.3   | 1,157.22 | 14.63       |
| Advanced     | For some reason, the assistant is... | 1,377.93 | 1,514.38 | 1,449.14  | 1,448.96 | 52.77       |

## AWS `inf1.xlarge` instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | Make an SQL insert statement...      | 112.86   | 139.02   | 118.21    | 112.93 | 11.63       |
| Basic        | For some reason, the assistant is... | 164.84   | 171.22   | 166.99    | 166.71 | 2.6         |
| Intermediate | Make an SQL insert statement...      | 312.64   | 321.35   | 314.9     | 313.26 | 3.65        |
| Intermediate | For some reason, the assistant is... | 399.14   | 540.05   | 471.80    | 474.01 | 55.17       |
| Advanced     | Make an SQL insert statement...      | 564.13   | 612.13   | 574.33    | 564.80 | 21.15       |
| Advanced     | For some reason, the assistant is... | 665.89   | 729.69   | 694.36    | 689.37 | 25.19       |

## AWS `g5.xlarge` (one GPU) instance

| Test Type    | Prompt (Trimmed)                     | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|--------------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | Make an SQL insert statement...      | 170.26   | 195.82   | 175.55    | 170.55 | 11.33       |
| Basic        | For some reason, the assistant is... | 253.73   | 254.86   | 254.03    | 253.84 | 0.47        |
| Intermediate | Make an SQL insert statement...      | 190.79   | 236.65   | 200.25    | 191.0  | 20.35       |
| Intermediate | For some reason, the assistant is... | 274.39   | 275.61   | 274.99    | 275.0  | 0.44        |
| Advanced     | Make an SQL insert statement...      | 208.22   | 209.8    | 208.72    | 208.41 | 0.63        |
| Advanced     | For some reason, the assistant is... | 292.70   | 294.24   | 293.2     | 292.99 | 0.51        |
