# Installing LLM Guard

## Prerequisites

Supported Python versions:

- 3.9
- 3.10
- 3.11

## Using `pip`

!!! note

    Consider installing the LLM Guard python packages on a virtual environment like `venv` or `conda`.

```bash
pip install llm-guard
```

If you have issue installing the package due to missing `torch`, you can try the following commands:

```bash
pip install wheel
pip install torch==2.0.1
pip install llm-guard --no-build-isolation
```

## Install from source

To install LLM Guard from source, first clone the repo:

- Using HTTPS
```bash
git clone https://github.com/protectai/llm-guard.git
```
- Using SSH
```bash
git clone git@github.com:protectai/llm-guard.git
```

We recommend to use a virtual environment like `venv` or `conda` to install the package.

```bash
python -m venv venv
source venv/bin/activate
```

Then, install the package using `pip`:

```bash
python -m pip install ".[dev]"
```
