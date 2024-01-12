# Ban Competitors Scanner

The `BanCompetitors` scanner is designed to prevent the inclusion of competitor names in the prompts submitted by users.
This scanner ensures that prompts containing references to known competitors are either flagged or altered, according to user settings, to maintain a strict focus on the user's own products or services.

## Motivation

In business and marketing contexts, it's important to avoid inadvertently promoting or acknowledging competitors.
With the increasing use of LLMs for generating content, there's a risk that user-provided prompts might contain competitor names, leading to outputs that promote those competitors.

The `BanCompetitors` mitigates this risk by analyzing prompts for competitor mentions and taking appropriate action.

## How it works

The scanner uses a Named Entity Recognition (NER) model to identify organizations within the text.
After extracting these entities, it cross-references them with a user-provided list of known competitors, which should include all common variations of their names.
If a competitor is detected, the scanner can either flag the text or redact the competitor's name based on user preference.

Models:
- [tomaarsen/span-marker-bert-small-orgs](https://huggingface.co/tomaarsen/span-marker-bert-small-orgs)
- [tomaarsen/span-marker-bert-base-orgs](https://huggingface.co/tomaarsen/span-marker-bert-base-orgs)

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

- **Accuracy**: The accuracy of competitor detection relies heavily on the NER model's capabilities and the comprehensiveness of the competitor list.
- **Context Awareness**: The scanner may not fully understand the context in which a competitor's name is used, leading to potential over-redaction.
- **Performance**: The scanning process might add additional computational overhead, especially for large texts with numerous entities.

## Optimization Strategies

ONNX support for this scanner is currently in development ([PR](https://github.com/tomaarsen/SpanMarkerNER/pull/43)).

## Benchmark

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input BanCompetitors
```

Results:

WIP
