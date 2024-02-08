# Reading Time Scanner

This scanner estimates and manages the reading time of text content.
It is particularly useful for applications where content length and reading time need to be controlled, such as in
educational materials or time-sensitive reading platforms.

## Use Case

- **Educational** Content: Ensuring reading assignments fit within class durations.
- **Content Publishing**: Tailoring articles or stories to fit expected reading times for specific audiences.

## How it works

- **Estimates Reading Time**: Calculates the time required to read a given text based on average reading speed (200
  words per minute).
- **Truncates Text to Fit Time Limit**: If the text exceeds a specified reading time threshold, the scanner can truncate
  it to fit within the limit.

## Usage

```python
from llm_guard.output_scanners import ReadingTime

scanner = ReadingTime(max_time=5, truncate=True)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input length: 14
- Test times: 5

Run the following script:

```sh
python benchmarks/run.py output ReadingTime
```

Results:

| Instance          | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS        |
|-------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|------------|
| AWS m5.xlarge     | 0.00             | 0.11                  | 0.13                  | 0.14                  | 0.07                 | 3409584.03 |
| AWS g5.xlarge GPU | 0.00             | 0.12                  | 0.13                  | 0.13                  | 0.08                 | 3045052.33 |
