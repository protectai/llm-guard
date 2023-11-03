# Installing LLM Guard

This document describes how to download and install the LLM Guard locally.

## Supported Python Versions

LLM Guard is supported for the following python versions:

- 3.9
- 3.10
- 3.11

## Using `pip`

!!! note

    Consider installing the LLM Guard python packages on a virtual environment like `venv` or `conda`.

```bash
pip install llm-guard
```

## Install from source

To install LLM Guard from source, first clone the repo:

- Using HTTPS
```bash
git clone https://github.com/laiyer-ai/llm-guard.git
```
- Using SSH
```bash
git clone git@github.com:laiyer-ai/llm-guard.git
```

Then, install the package using `pip`:

```bash
# install the repo
pip install -U -r requirements.txt -r requirements-dev.txt
python setup.py install
```
