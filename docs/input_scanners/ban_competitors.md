# Ban Competitors Scanner

The `BanCompetitors` scanner is designed to prevent the inclusion of competitor names in the prompts submitted by users.
This scanner ensures that prompts containing references to known competitors are either flagged or altered, according to
user settings, to maintain a strict focus on the user's own products or services.

## Motivation

In business and marketing contexts, it's important to avoid inadvertently promoting or acknowledging competitors.
With the increasing use of LLMs for generating content, there's a risk that user-provided prompts might contain
competitor names, leading to outputs that promote those competitors.

The `BanCompetitors` mitigates this risk by analyzing prompts for competitor mentions and taking appropriate action.

## How it works

The scanner uses a Named Entity Recognition (NER) model to identify organizations within the text.
After extracting these entities, it cross-references them with a user-provided list of known competitors, which should
include all common variations of their names.
If a competitor is detected, the scanner can either flag the text or redact the competitor's name based on user
preference.

Models:

- [guishe/nuner-v1_orgs](https://huggingface.co/guishe/nuner-v1_orgs)

## Usage

```python
from llm_guard.input_scanners import BanCompetitors

competitor_list = ["Competitor1", "CompetitorOne", "C1", ...]  # Extensive list of competitors
scanner = BanCompetitors(competitors=competitor_list, redact=False, threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

**An effective competitor list should include:**

- The official names of all known competitors.
- Common abbreviations or variations of these names.
- Any subsidiaries or associated brands of the competitors.
- The completeness and accuracy of this list are vital for the effectiveness of the scanner.

## Considerations and Limitations

- **Accuracy**: The accuracy of competitor detection relies heavily on the NER model's capabilities and the
  comprehensiveness of the competitor list.
- **Context Awareness**: The scanner may not fully understand the context in which a competitor's name is used, leading
  to potential over-redaction.
- **Performance**: The scanning process might add additional computational overhead, especially for large texts with
  numerous entities.

## Optimization Strategies

[Read more](../tutorials/optimization.md)

## Benchmark

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input BanCompetitors
```

Results:

| Instance             | Latency Variance | Latency 90 Percentile | Latency 95 Percentile | Latency 99 Percentile | Average Latency (ms) | QPS    |
|----------------------|------------------|-----------------------|-----------------------|-----------------------|----------------------|--------|
| AWS m5.xlarge        | 2.85             | 616.51                | 642.39                | 663.09                | 561.55               | 149.59 |
| AWS g5.xlarge GPU    | 26.72            | 274.92                | 356.44                | 421.66                | 111.01               | 756.69 |
| AWS r6a.xlarge (AMD) | 0.44             | 646.05                | 650.56                | 654.17                | 620.68               | 135.34 |
