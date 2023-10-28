# Output scanners benchmarks

## How to run

Choose scanner you would like to evaluate, and run the following command:

```sh
python benchmarks/run.py output NoRefusal
```

Output example:

```json
{
    "Scanner": "NoRefusal",
    "Scanner Type": "output",
    "Time Taken (seconds)": 0.42,
    "Total Length Processed": 47,
    "Characters per Second": 111.78
}
```

## Test environment

- Platform: Amazon Linux 2
- Python Version: 3.10.2

## Setup

- Basic scanners: [Deanonymize](../output_scanners/deanonymize.md), [Secrets](../output_scanners/sensitive.md).
- Intermediate
  scanners: [Deanonymize](../output_scanners/deanonymize.md), [Secrets](../output_scanners/sensitive.md), [Bias](../output_scanners/bias.md), [Toxicity](../output_scanners/toxicity.md).
- Advanced scanners: All scanners.

## AWS `m5.large` instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 21.97    | 138.84   | 45.95     | 22.72    | 51.92       |
| Intermediate | INSERT INTO users (Name, Email... | 425.03   | 453.74   | 432.54    | 426.46   | 12.1        |
| Advanced     | INSERT INTO users (Name, Email... | 2,461.36 | 2,475.16 | 2,468.23  | 2,469.19 | 5.24        |

## AWS `inf1.xlarge` instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median   | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|----------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 23.61    | 148.28   | 48.79     | 24.03    | 55.61       |
| Intermediate | INSERT INTO users (Name, Email... | 225.65   | 250.33   | 232.49    | 227.83   | 10.29       |
| Advanced     | INSERT INTO users (Name, Email... | 1,312.75 | 1,332.89 | 1,324.19  | 1,325.75 | 7.53        |

## AWS `g5.xlarge` (one GPU) instance

| Test Type    | Prompt (Trimmed)                  | Min (ms) | Max (ms) | Mean (ms) | Median | StdDev (ms) |
|--------------|-----------------------------------|----------|----------|-----------|--------|-------------|
| Basic        | INSERT INTO users (Name, Email... | 19.45    | 102.61   | 36.57     | 36.92  | 164.59      |
| Intermediate | INSERT INTO users (Name, Email... | 34.6     | 80.417   | 44.24     | 12.44  | 35.09       |
| Advanced     | INSERT INTO users (Name, Email... | 708.79   | 719.14   | 711.84    | 710.65 | 4.18        |
