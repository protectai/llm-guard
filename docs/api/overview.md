# API

LLM Guard can be deployed as an API. We rely on [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://www.uvicorn.org/) to serve the API.

## Configuration

All configurations are stored in `config/scanners.yml`. It supports configuring via environment variables.

!!! note

    Scanners will be executed in the order of configuration.

### Default environment variables

- `LOG_LEVEL` (bool): Log level. Default is `INFO`. If set as `DEBUG`, debug mode will be enabled, which makes Swagger UI available.
- `CACHE_MAX_SIZE` (int): Maximum number of items in the cache. Default is unlimited.
- `CACHE_TTL` (int): Time in seconds after which a cached item expires. Default is 1 hour.
- `SCAN_FAIL_FAST` (bool): Stop scanning after the first failed check. Default is `False`.
- `SCAN_PROMPT_TIMEOUT` (int): Time in seconds after which a prompt scan will timeout. Default is 10 seconds.
- `SCAN_OUTPUT_TIMEOUT` (int): Time in seconds after which an output scan will timeout. Default is 30 seconds.
- `APP_PORT` (int): Port to run the API. Default is `8000`.

### Best practices

1. Enable `SCAN_FAIL_FAST` to avoid unnecessary scans.
2. Enable `CACHE_MAX_SIZE` and `CACHE_TTL` to cache results and avoid unnecessary scans.
3. Enable authentication and rate limiting to avoid abuse.
4. Enable lazy loading of models to avoid failed HTTP probes.
5. Enable load of models from a directory to avoid downloading models each time the container starts.

### Load models from a directory

It's possible to load models from a local directory.
You can set `model_path` in each supported scanner with the folder to the ONNX version of the model.

This way, the models won't be downloaded each time the container starts.

[Relevant notebook](../tutorials/notebooks/local_models.ipynb)

### Lazy loading

You can enable `lazy_load` in the YAML config file to load models only on the first request instead of the API start.
That way, you can avoid failed HTTP probes due to the long model loading time.

## Observability

There are built-in environment variables to configure observability:

- [FastAPI Instrumentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html)
- [OpenTelemetry](https://opentelemetry.io/)

### Logging

Logs are written to `stdout` in a structured format, which can be easily parsed by log management systems.

### Metrics

The following exporters are available for metrics:

- **Console (console)**: Logs metrics to `stdout`.
- **Prometheus (prometheus)**: Exposes metrics on `/metrics` endpoint.
- **OpenTelemetry (otel_http)**: Sends metrics to an OpenTelemetry collector via HTTP endpoint.

### Tracing

The following exporters are available for tracing:

- **Console (console)**: Logs traces to `stdout`
- **OpenTelemetry (otel_http)**: Sends traces to an OpenTelemetry collector via HTTP endpoint.
- **AWS X-Ray (xray)**: Sends traces to OpenTelemetry collector in the AWS X-Ray format.
