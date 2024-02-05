# Contributing

:tada: Thanks for taking the time to contribute! :tada:

## Reporting Issues

If you would like to report a bug, request a new feature or enhancement, follow [this link](https://github.com/protectai/llm-guard/issues/new/choose).

## Submitting Changes

1. Fork the repository on GitHub.
2. Make the changes to your forked repository.
3. When you are finished making changes or improvements, create a pull request from your forked repository to our original repository.
4. The core team will review your pull request and provide feedback.

## Project Setup

```bash
# clone the repo
git clone -b dev https://github.com/protectai/llm-guard.git
cd llm-guard

# create a virtual environment
python -m venv venv
source venv/bin/activate

# install the repo
python -m pip install ".[dev]"

# download SpaCy model
python -m spacy download en_core_web_trf
```

## Testing

Our project uses [pytest](https://docs.pytest.org/en/latest/) for testing. Make sure that all tests pass before you submit a pull request.

```bash
python -m pytest --exitfirst --verbose --failed-first --cov=.
python -m coverage run -m pytest .
```

## Code Style

We use `black` code style.

You can run `pre-commit run --all-files` to run all linters.

## Documentation

If you are adding a new feature or changing the existing functionality, please include corresponding changes in the documentation.

Thank you for making our project better. We appreciate your effort and look forward to your contribution!
