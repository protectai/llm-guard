# Attacks

This section outlines the range of attacks that can be launched against Large Language Models (LLMs) and demonstrates how LLM Guard offers robust protection against these threats.

## NIST Trustworthy and Responsible AI

Following the [NIST Trustworthy and Responsible AI framework](https://doi.org/10.6028/NIST.AI.100-2e2023), attacks on Generative AI systems, including LLMs, can be broadly categorized into four types.
LLM Guard is designed to counteract each category effectively:

### 1. Availability Breakdowns

Attacks targeting the availability of LLMs aim to disrupt their normal operations. Methods such as Denial of Service (DoS) attacks are common. LLM Guard combats these through:

- [TokenLimit Input](../input_scanners/token_limit.md)
- ...

### 2. Integrity Violations

These attacks attempt to undermine the integrity of LLMs, often by injecting malicious prompts. LLM Guard safeguards integrity through various scanners, including:

- [Prompt Injection](../input_scanners/prompt_injection.md)
- Language [Input](../input_scanners/language.md) & [Output](../output_scanners/language.md)
- [Language Same](../output_scanners/language_same.md)
- [Relevance Output](../output_scanners/relevance.md)
- [Factual Consistency Output](../output_scanners/factual_consistency.md)
- Ban Topics [Input](../input_scanners/ban_topics.md) & [Output](../output_scanners/ban_topics.md)
- ...

### 3. Privacy Compromise

These attacks seek to compromise privacy by extracting sensitive information from LLMs. LLM Guard protects privacy through:

- [Anonymize Input](../input_scanners/anonymize.md)
- [Sensitive Output](../output_scanners/sensitive.md)
- [Secrets Input](../input_scanners/secrets.md)
- ...

### 4. Abuse

Abuse attacks involve the generation of harmful content using LLMs. LLM Guard mitigates these risks through:

- [Bias Output](../output_scanners/bias.md)
- Toxicity [Input](../input_scanners/toxicity.md) & [Output](../output_scanners/toxicity.md)
- Ban Competitors [Input](../input_scanners/ban_competitors.md) & [Output](../output_scanners/ban_competitors.md)
- ...

LLM Guard's suite of scanners comprehensively addresses each category of attack, providing a multi-layered defense mechanism to ensure the safe and responsible use of LLMs.
