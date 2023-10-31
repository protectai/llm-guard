# LanguageSame Scanner

This scanner evaluates and checks if the prompt and output are in the same language.

## Attack

There can be cases where the model produces an output in a different language than the input or prompt. This can be
unintended, especially in applications that require consistent language output.

The `LanguageSame` Scanner serves to identify these discrepancies and helps in maintaining consistent linguistic
outputs.

## How it works

The scanner predominantly utilizes the [fasttext-langdetect](https://github.com/zafercavdar/fasttext-langdetect/) library to discern the
language of both the input prompt and the output.

!!! info

    Supported languages: `af als am an ar arz as ast av az azb ba bar bcl be bg bh bn bo bpy br bs bxr ca cbk ce cebckb
    co cs cv cy da de diq dsb dty dv el eml en eo es et eu fa fi fr frr fy ga gd gl gn gom gu gv he hi hif hr hsb ht hu
    hy ia id ie ilo io is it ja jbo jv ka kk km kn ko krc ku kv kw ky la lb lez li lmo lo lrc lt lv mai mg mhr min mk ml
    mn mr mrj ms mt mwl my myv mzn nah nap nds ne new nl nn no oc or os pa pam pfl pl pms pnb ps pt qu rm ro ru rue sa
    sah sc scn sco sd sh si sk sl so sq sr su sv sw ta te tg th tk tl tr tt tyv ug uk ur uz vec vep vi vls vo wa war
    wuu xal xmf yi yo yue zh`.

It then checks whether both detected languages are the same. If they are not, it indicates a potential language
discrepancy.

!!! note

    While the scanner identifies language discrepancies, it doesn't limit or enforce any specific language sets. Instead, it simply checks for language consistency between the prompt and output. If you want to enforce languages, use Language scanner

## Usage

```python
from llm_guard.output_scanners import LanguageSame

scanner = LanguageSame()
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py output LanguageSame
```

Results:

| Instance          | Time taken, s | Characters per Second | Total Length Processed |
|-------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS) | 0.387         | 36.14                 | 14                     |
| m5.large (AWS)    | 0.42          | 33.31                 | 14                     |
