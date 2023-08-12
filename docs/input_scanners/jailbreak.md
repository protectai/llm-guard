# Jailbreak Scanner

Designed to detect attempts to elicit sensitive or inappropriate responses from the language model. These attempts, also
known as "jailbreak" attacks, aim to manipulate the model in ways that contravene service policies.

## Attack

Jailbreak attacks are meticulously crafted efforts to coerce unintended information or behavior from large language
models (LLM). These tactics can lead to a myriad of undesired outcomes, such as unveiling sensitive data or prompting
inappropriate reactions, breaching platform norms and regulations.

As specified by the `OWASP Top 10 LLM attacks`, this vulnerability is categorized under:

[LLM08: Excessive Agency](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - LLM-driven
platforms might unexpectedly perform actions that culminate in unanticipated repercussions. This predicament stems from
bestowing undue functionalities, privileges, or autonomy upon the LLM systems. The Jailbreak scanner assists in
mitigating this by restraining the LLM's potential actions.

## How it works

The Jailbreak Scanner employs
the [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model from
Hugging Face to assess the similarity between input prompts and a dataset populated with familiar jailbreak attack
strategies.

While the dataset is nascent, it's continually enriched, drawing from repositories of known attack patterns, notably
from platforms like [JailbreakChat](https://www.jailbreakchat.com/).

## Usage

```python
from llm_guard.input_scanners import Jailbreak

scanner = Jailbreak(threshold=0.5)
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```
