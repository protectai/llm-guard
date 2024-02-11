import argparse
import asyncio
import concurrent.futures
import time
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from llm_guard import scan_output, scan_prompt
from llm_guard.vault import Vault

from .cache import InMemoryCache
from .config import AuthConfig, get_config, get_input_scanners, get_output_scanners
from .otel import instrument_app
from .schemas import (
    AnalyzeOutputRequest,
    AnalyzeOutputResponse,
    AnalyzePromptRequest,
    AnalyzePromptResponse,
)
from .util import configure_logger
from .version import __version__

vault = Vault()

parser = argparse.ArgumentParser(description="LLM Guard API")
parser.add_argument("config", type=str, help="Path to the configuration file")
args = parser.parse_args()
scanners_config_file = args.config

config = get_config(scanners_config_file)

LOGGER = structlog.getLogger(__name__)
log_level = config.app.log_level
is_debug = log_level == "DEBUG"
configure_logger(log_level)

input_scanners = get_input_scanners(config.input_scanners, vault)
output_scanners = get_output_scanners(config.output_scanners, vault)


def create_app():
    cache = InMemoryCache(
        max_size=config.cache.max_size,
        expiration_time=config.cache.ttl,
    )

    if config.app.scan_fail_fast:
        LOGGER.debug("Scan fail_fast mode is enabled")

    app = FastAPI(
        title=config.app.name,
        description="API to run LLM Guard scanners.",
        debug=is_debug,
        version=__version__,
        openapi_url="/openapi.json" if is_debug else None,  # hide docs in production
    )

    register_routes(app, cache, input_scanners, output_scanners)

    return app


def _check_auth_function(auth_config: AuthConfig) -> callable:
    async def check_auth_noop() -> bool:
        return True

    if not auth_config:
        return check_auth_noop

    if auth_config.type == "http_bearer":
        credentials_type = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
    elif auth_config.type == "http_basic":
        credentials_type = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]
    else:
        raise ValueError(f"Invalid auth type: {auth_config.type}")

    async def check_auth(credentials: credentials_type) -> bool:
        if auth_config.type == "http_bearer":
            if credentials.credentials != auth_config.token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
                )
        elif auth_config.type == "http_basic":
            if (
                credentials.username != auth_config.username
                or credentials.password != auth_config.password
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username or Password"
                )

        return True

    return check_auth


def register_routes(
    app: FastAPI, cache: InMemoryCache, input_scanners: list, output_scanners: list
):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type"],
    )

    limiter = Limiter(key_func=get_remote_address, default_limits=[config.rate_limit.limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    if bool(config.rate_limit.enabled):
        app.add_middleware(SlowAPIMiddleware)

    check_auth = _check_auth_function(config.auth)

    @app.get("/", tags=["Main"])
    @limiter.exempt
    async def read_root():
        return {"name": "LLM Guard API"}

    @app.get("/healthz", tags=["Health"])
    @limiter.exempt
    async def healthcheck():
        return JSONResponse({"status": "alive"})

    @app.get("/readyz", tags=["Health"])
    @limiter.exempt
    async def liveliness():
        return JSONResponse({"status": "ready"})

    @app.post(
        "/analyze/output",
        tags=["Analyze"],
        response_model=AnalyzeOutputResponse,
        status_code=status.HTTP_200_OK,
        description="Analyze an output and return the sanitized output and the results of the scanners",
    )
    @limiter.limit("5/minute")
    async def analyze_output(
        request: AnalyzeOutputRequest, _: Annotated[bool, Depends(check_auth)]
    ) -> AnalyzeOutputResponse:
        LOGGER.debug("Received analyze output request", request=request)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            try:
                start_time = time.time()
                sanitized_output, results_valid, results_score = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        scan_output,
                        output_scanners,
                        request.prompt,
                        request.output,
                        config.app.scan_fail_fast,
                    ),
                    timeout=config.app.scan_output_timeout,
                )

                response = AnalyzeOutputResponse(
                    sanitized_output=sanitized_output,
                    is_valid=all(results_valid.values()),
                    scanners=results_score,
                )
                elapsed_time = time.time() - start_time
                LOGGER.debug(
                    "Sanitized response",
                    scores=results_score,
                    elapsed_time_seconds=round(elapsed_time, 6),
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
                )

        return response

    @app.post(
        "/analyze/prompt",
        tags=["Analyze"],
        response_model=AnalyzePromptResponse,
        status_code=status.HTTP_200_OK,
        description="Analyze a prompt and return the sanitized prompt and the results of the scanners",
    )
    async def analyze_prompt(
        request: AnalyzePromptRequest,
        _: Annotated[bool, Depends(check_auth)],
        response: Response,
    ) -> AnalyzePromptResponse:
        LOGGER.debug("Received analyze prompt request", request=request)

        cached_result = cache.get(request.prompt)
        if cached_result:
            LOGGER.debug("Response was found in cache")

            response.headers["X-Cache-Hit"] = "true"

            return AnalyzePromptResponse(**cached_result)

        response.headers["X-Cache-Hit"] = "false"

        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            try:
                start_time = time.time()
                sanitized_prompt, results_valid, results_score = await asyncio.wait_for(
                    loop.run_in_executor(
                        executor,
                        scan_prompt,
                        input_scanners,
                        request.prompt,
                        config.app.scan_fail_fast,
                    ),
                    timeout=config.app.scan_prompt_timeout,
                )

                response = AnalyzePromptResponse(
                    sanitized_prompt=sanitized_prompt,
                    is_valid=all(results_valid.values()),
                    scanners=results_score,
                )
                cache.set(request.prompt, response.dict())

                elapsed_time = time.time() - start_time
                LOGGER.debug(
                    "Sanitized prompt response returned",
                    scores=results_score,
                    elapsed_time_seconds=round(elapsed_time, 6),
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
                )

        return response

    if config.metrics and config.metrics.exporter == "prometheus":

        @app.get("/metrics", tags=["Metrics"])
        @limiter.exempt
        async def metrics():
            return Response(
                content=generate_latest(REGISTRY), headers={"Content-Type": CONTENT_TYPE_LATEST}
            )

    @app.on_event("shutdown")
    async def shutdown_event():
        LOGGER.info("Shutting down app...")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        LOGGER.warning(
            "HTTP exception", exception_status_code=exc.status_code, exception_detail=exc.detail
        )

        return JSONResponse(
            {"message": str(exc.detail), "details": None}, status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        LOGGER.warning("Invalid request", exception=str(exc))

        response = {"message": "Validation failed", "details": exc.errors()}
        return JSONResponse(
            jsonable_encoder(response), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


app = create_app()
instrument_app(app, config.app.name, config.tracing, config.metrics)


def run_app():
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.app.port,
        server_header=False,
        log_level=log_level.lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=2,
    )
