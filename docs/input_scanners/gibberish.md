# Gibberish Scanner

This scanner is designed to identify and filter out gibberish or nonsensical inputs in English language text.

It proves invaluable in applications that require coherent and meaningful user inputs, such as chatbots and automated processing systems.

## Attack scenario

Gibberish is defined as text that is either completely nonsensical or so poorly structured that it fails to convey a meaningful message.
It includes random strings of words, sentences laden with grammatical or syntactical errors, and text that, while appearing structured, lacks logical coherence.

Instances of gibberish in user inputs can significantly disrupt the operation of digital platforms, potentially leading to degraded performance or exploitation of system vulnerabilities.
By effectively identifying and excluding gibberish, the scanner helps maintain the platform's integrity and ensures a seamless user experience.

## How it works

Utilizing the model [madhurjindal/autonlp-Gibberish-Detector-492513457](https://huggingface.co/madhurjindal/autonlp-Gibberish-Detector-492513457), this scanner is capable of distinguishing between meaningful English text and gibberish. This functionality is critical for enhancing the performance and reliability of systems that depend on accurate and coherent user inputs.

## Usage

```python
from llm_guard.input_scanners import Gibberish
from llm_guard.input_scanners.gibberish import MatchType

scanner = Gibberish(match_type=MatchType.FULL)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Optimization Strategies

[Read more](../get_started/optimization.md)

## Benchmarks

Test setup:

- Platform: Amazon Linux 2
- Python Version: 3.11.6
- Input Length: 248
- Test Times: 5

Run the following script:

```sh
python benchmarks/run.py input Gibberish
```

Results:

WIP
