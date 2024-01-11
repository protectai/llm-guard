# API

This example demonstrates how to use LLM Guard as an API. It uses [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://www.uvicorn.org/) to serve the API.

## Usage

## From source

1. Copy the code from [llm_guard_api](https://github.com/laiyer-ai/llm-guard/tree/main/llm_guard_api)

2. Install dependencies (preferably in a virtual environment)
```sh
python -m pip install "."
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
make build-docker-multi
make run-docker
```

## Configuration

### Environment variables

- `DEBUG` (bool): Enable debug mode
- `CACHE_MAX_SIZE` (int): Maximum number of items in the cache. Default is unlimited.
- `CACHE_TTL` (int): Time in seconds after which a cached item expires. Default is 1 hour.
- `SCAN_FAIL_FAST` (bool): Stop scanning after the first failed check. Default is `False`.
- `SCAN_PROMPT_TIMEOUT` (int): Time in seconds after which a prompt scan will timeout. Default is 10 seconds.
- `SCAN_OUTPUT_TIMEOUT` (int): Time in seconds after which an output scan will timeout. Default is 30 seconds.
- `USE_ONNX` (bool): Use ONNX models instead of PyTorch on CPU (faster inference). Default is `True`.

### Scanners

You can configure scanners in `scanners.yml` referring to their names and parameters.

Scanners will be executed in the order of configuration.

### Best practices

1. Enable `SCAN_FAIL_FAST` to avoid unnecessary scans.
2. Enable `USE_ONNX` to speed up inference on CPU.
3. Enable `CACHE_MAX_SIZE` and `CACHE_TTL` to cache results and avoid unnecessary scans.

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

## Troubleshooting

### Out-of-memory error

If you get an out-of-memory error, you can change `config.yml` file to use less scanners.

## Schema

<swagger-ui src="https://raw.githubusercontent.com/laiyer-ai/llm-guard/main/llm_guard_api/openapi.json" />
