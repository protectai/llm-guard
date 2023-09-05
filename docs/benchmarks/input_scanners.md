# Input scanners benchmarks

!!! info

    Reference code: https://github.com/laiyer-ai/llm-guard/blob/main/benchmarks/scan_prompt_latency.py

## Test environment

- Platform: Linux
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

## AWS `` (GPU) instance

TBD
