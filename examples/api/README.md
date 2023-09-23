# LLM Guard API

A simple `fastapi`-based API to run LLM Guard checks.

## Installation

1. Clone the repo and move to the `examples/api` folder

2. Install dependencies (preferably in a virtual environment)

```sh
pip install -r requirements.txt
```

Or you can use Makefile

```sh
make install
```

3. Run the API:

```sh
make run
```

Or you can run it using Docker:

```sh
make run-docker
```

## Configuration

### Environment variables

- `DEBUG` (bool): Enable debug mode
- `CACHE_MAX_SIZE` (int): Maximum number of items in the cache. Default is unlimited.
- `CACHE_TTL` (int): Time in seconds after which a cached item expires. Default is 1 hour.
- `SCAN_FAIL_FAST` (bool): Stop scanning after the first failed check. Default is `False`.

### Scanners

You can configure scanners in `scanners.yml` referring to their names and parameters.

Scanners will be executed in the order of configuration.

## Deploy Docker

We have an officially supported image on [Docker Hub](https://hub.docker.com/repository/docker/laiyer/llm-guard-api/general).

### Download Docker image

```sh
docker pull laiyer/llm-guard-api
```

#### Run container with default port

```sh
docker run -d -p 8001:8000 -e DEBUG='false' laiyer/llm-guard-api:latest
```
