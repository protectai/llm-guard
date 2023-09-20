# API

This example demonstrates how to use LLM Guard as an API.

## Usage

## Installation

1. Copy the code from [examples/api](https://github.com/laiyer-ai/llm-guard/tree/main/examples/api)

2. Install dependencies (preferably in a virtual environment)

```sh
pip install -r requirements.txt
```

Or you can use Makefile

```sh
make install
```

3. Run the API locally:

```sh
make run
```

Or you can run it using Docker:

```sh
make run-docker
```

## Configuration

It can be configured using environment variables:

- `DEBUG` (bool): Enable debug mode
- `CACHE_MAX_SIZE` (int): Maximum number of items in the cache. Default is unlimited.
- `CACHE_TTL` (int): Time in seconds after which a cached item expires. Default is 1 hour.

Also, you can configure scanners in `config.yml` referring to their names and parameters.
