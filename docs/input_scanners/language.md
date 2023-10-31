# Language Scanner

This scanner identifies and assesses the authenticity of the language used in prompts.

## Attack

With the rise of sophisticated LLMs, there has been an increase in attempts to manipulate or "confuse" these models.
Some common tactics employed by users to attack LLMs include:

- **Jailbreaks and Prompt Injections in different languages**. For example, by utilizing unique aspects of the Japanese
  language to try and confuse the model.
- **Encapsulation & Overloading**: Using excessive code or surrounding prompts with a plethora of special characters to
  overload or trick the model.

The Language Scanner is designed to identify such attempts, assess the authenticity of the language used.

## How it works

At its core, the scanner leverages the capabilities of [fasttext-langdetect](https://github.com/zafercavdar/fasttext-langdetect/) library.
The primary function of the scanner is to analyze the input prompt, determine its language, and check if it's in the
list.

!!! info

    Supported languages: `af als am an ar arz as ast av az azb ba bar bcl be bg bh bn bo bpy br bs bxr ca cbk ce cebckb co
    cs cv cy da de diq dsb dty dv el eml en eo es et eu fa fi fr frr fy ga gd gl gn gom gu gv he hi hif hr hsb ht hu hy ia
    id ie ilo io is it ja jbo jv ka kk km kn ko krc ku kv kw ky la lb lez li lmo lo lrc lt lv mai mg mhr min mk ml mn mr
    mrj ms mt mwl my myv mzn nah nap nds ne new nl nn no oc or os pa pam pfl pl pms pnb ps pt qu rm ro ru rue sa sah sc
    scn sco sd sh si sk sl so sq sr su sv sw ta te tg th tk tl tr tt tyv ug uk ur uz vec vep vi vls vo
    wa war wuu xal xmf yi yo yue zh`.

## Usage

```python
from llm_guard.input_scanners import Language

scanner = Language(valid_languages=["en", ...])  # Add other valid languages as needed
sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
```

## Benchmarks

Environment:

- Platform: Amazon Linux 2
- Python Version: 3.11.6

Run the following script:

```sh
python benchmarks/run.py input Language
```

Results:

| Instance                | Time taken, s | Characters per Second | Total Length Processed |
|-------------------------|---------------|-----------------------|------------------------|
| inf1.xlarge (AWS)       | 0.4           | 34.98                 | 14                     |
| m5.large (AWS)          | 0.36          | 37.9                  | 14                     |
| g5.xlarge (AWS) **GPU** | 0.314         | 44.63                 | 14                     |
