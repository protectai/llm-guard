# API

This example demonstrates how to use LLM Guard as an API. We rely on [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://www.uvicorn.org/) to serve the API.

## Usage

### From source

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

4. Run the API locally:
```bash
make run
```

### From Docker

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
docker run -d -p 8000:8000 -e LOG_LEVEL='DEBUG' -e API_TOKEN='my-token' laiyer/llm-guard-api:latest
```

This will start the API on port 8000. You can now access the API at `http://localhost:8000/swagger.json`.

If you want to use a custom configuration, you can mount a volume to `/home/user/app/config`:

```bash
docker run -d -p 8000:8000 -e LOG_LEVEL='INFO' -v ./config:/home/user/app/config laiyer/llm-guard-api:latest
```

!!! warning

    We recommend at least 16GB of RAM allocated to Docker. We are working on optimizing the memory usage when the container starts.

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

## Client

### Python

```python title="sync_llm_guard_client.py" linenums="1"
import os
import requests

LLM_GUARD_API_KEY = os.environ.get("LLM_GUARD_API_KEY")
LLM_GUARD_BASE_URL = os.environ.get("LLM_GUARD_URL")

class LLMGuardMaliciousPromptException(Exception):
    scores = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.scores = kwargs.get("scores", {})

    def __str__(self):
        scanners = [scanner for scanner, score in self.scores.items() if score > 0]

        return f"LLM Guard detected a malicious prompt. Scanners triggered: {', '.join(scanners)}; scores: {self.scores}"


class LLMGuardRequestException(Exception):
    pass

def request_llm_guard_prompt(prompt: str):
    try:
        response = requests.post(
            url=f"{LLM_GUARD_BASE_URL}/analyze/prompt",
            json={"prompt": prompt},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LLM_GUARD_API_KEY}",
            },
            ssl=False,
        )

        response_json = response.json()
    except requests.RequestException as err:
        raise LLMGuardRequestException(err)

    if not response_json["is_valid"]:
        raise LLMGuardMaliciousPromptException(scores=response_json["scanners"])

    return response_json["sanitized_prompt"]

prompt = "Write a Python function to calculate the factorial of a number."
sanitized_prompt = request_llm_guard_prompt(prompt)
print(sanitized_prompt)
```

Alternatively, you can call LLM provider and LLM Guard API in parallel:

```python title="async_llm_guard_client.py" linenums="1"
import os
import asyncio
import aiohttp
from openai import AsyncOpenAI

LLM_GUARD_API_KEY = os.environ.get("LLM_GUARD_API_KEY")
LLM_GUARD_BASE_URL = os.environ.get("LLM_GUARD_URL")
openai_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
system_prompt = "You are a Python tutor."

class LLMGuardMaliciousPromptException(Exception):
    scores = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.scores = kwargs.get("scores", {})

    def __str__(self):
        scanners = [scanner for scanner, score in self.scores.items() if score > 0]

        return f"LLM Guard detected a malicious prompt. Scanners triggered: {', '.join(scanners)}; scores: {self.scores}"


class LLMGuardRequestException(Exception):
    pass

async def request_openai(prompt: str) -> str:
    chat_completion = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices[0].message.content


async def request_llm_guard_prompt(prompt: str):
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(
                url=f"{LLM_GUARD_BASE_URL}/analyze/prompt",
                json={"prompt": prompt},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LLM_GUARD_API_KEY}",
                },
                ssl=False,
                raise_for_status=True,
            )

            response_json = await response.json()
        except Exception as e:
            raise LLMGuardRequestException(e)

        if not response_json["is_valid"]:
            raise LLMGuardMaliciousPromptException(scores=response_json["scanners"])

async def generate_completion(prompt: str) -> str:
    result = await asyncio.gather(
        request_llm_guard_prompt(prompt),
        request_openai(prompt),
    )

    return result[1]

prompt = "Write a Python function to calculate the factorial of a number."
message = asyncio.run(
    generate_completion(prompt)
)
```

## Troubleshooting

### Out-of-memory error

If you get an out-of-memory error, you can change `config.yml` file to use less scanners.
Alternatively, you can enable `low_cpu_mem_usage` in scanners that rely on HuggingFace models.

## Swagger UI

<swagger-ui src="https://raw.githubusercontent.com/protectai/llm-guard/main/llm_guard_api/openapi.json" />
