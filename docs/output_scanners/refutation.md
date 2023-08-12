# Refutation Scanner

This scanner is designed to assess if the given content contradicts or refutes a certain statement or prompt. It acts as
a tool for ensuring the consistency and correctness of language model outputs, especially in contexts where logical
contradictions can be problematic.

## Attack

When interacting with users or processing information, it's important for a language model to not provide outputs that
directly contradict the given inputs or established facts. Such contradictions can lead to confusion or misinformation.
The scanner aims to highlight such inconsistencies in the output.

## How it works

The scanner leverages pretrained natural language inference (NLI) models from HuggingFace, such
as [ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli](https://huggingface.co/ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli) (
and other variants), to determine the relationship between a given prompt and the generated output.

A high contradiction score indicates that the output refutes the prompt.

This calculated refutation score is then compared to a pre-set threshold. Outputs that cross this threshold are flagged
as contradictory.

## Usage

```python
from llm_guard.output_scanners import Refutation

scanner = Refutation(threshold=0.7)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
