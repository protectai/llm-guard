# API Deployment

## From source

1. Copy the code from [llm_guard_api](https://github.com/protectai/llm-guard/tree/main/llm_guard_api)

2. Install dependencies (preferably in a virtual environment)
```bash
python -m pip install ".[cpu]"
python -m pip install ".[gpu]" # If you have a GPU
```

3. Alternatively, you can use Makefile:
```bash
make install
```

### Using uvicorn

Run the API locally:

```bash
make run
```

Or using CLI:

```bash
llm_guard_api ./config/scanners.yml
```

### Using gunicorn

In case you want to use `gunicorn` to run the API, you can use the following command:

```bash
gunicorn --workers 1 --preload --worker-class uvicorn.workers.UvicornWorker 'app.app:create_app(config_file="./config/scanners.yml")'
```

It will preload models in the shared memory among workers, which can be useful for performance.

## From Docker

Either build the Docker image or pull our official image from [Docker Hub](https://hub.docker.com/r/laiyer/llm-guard-api).

In order to build the Docker image, run the following command:

```bash
make build-docker-multi
make build-docker-cuda-multi # If you have a GPU
```

Or pull the official image:

```bash
docker pull laiyer/llm-guard-api:latest
```

Now, you can run the Docker container:

```bash
docker run -d -p 8000:8000 -e LOG_LEVEL='DEBUG' -e AUTH_TOKEN='my-token' laiyer/llm-guard-api:latest
```

This will start the API on port 8000. You can now access the API at `http://localhost:8000/swagger.json`.

If you want to use a custom configuration, you can mount a volume to `/home/user/app/config`:

```bash
docker run -d -p 8000:8000 -e APP_WORKERS=1 -e AUTH_TOKEN='my-token' -e LOG_LEVEL='DEBUG' -v ./entrypoint.sh:/home/user/app/entrypoint.sh -v ./config/scanners.yml:/home/user/app/config/scanners.yml laiyer/llm-guard-api:latest
```

!!! warning

    We recommend at least 16GB of RAM allocated to Docker. We are working on optimizing the memory usage when the container starts.

## Troubleshooting

### Out-of-memory error

If you get an out-of-memory error, you can change `config.yml` file to use less scanners.
Alternatively, you can enable `low_cpu_mem_usage` in scanners that rely on HuggingFace models.

### Failed HTTP probe

If you get a failed HTTP probe, it might be because the API is still starting. You can increase the `initialDelaySeconds` in the Kubernetes deployment.

Alternatively, you can configure `lazy_load` in the YAML config file to load models only on the first request.
