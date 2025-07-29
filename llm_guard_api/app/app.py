import asyncio
import concurrent.futures
import os
import time
from typing import Annotated, Callable, List

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
from llm_guard.input_scanners.base import Scanner as InputScanner
from llm_guard.output_scanners.base import Scanner as OutputScanner
from llm_guard.vault import Vault

from .config import AuthConfig, Config, get_config
from .otel import configure_otel, instrument_app
from .scanner import (
    InputIsInvalid,
    ascan_output,
    ascan_prompt,
    get_input_scanners,
    get_output_scanners,
    scanners_valid_counter,
)
from .schemas import (
    AnalyzeOutputRequest,
    AnalyzeOutputResponse,
    AnalyzePromptRequest,
    AnalyzePromptResponse,
    ScanOutputRequest,
    ScanOutputResponse,
    ScanPromptRequest,
    ScanPromptResponse,
)
from .util import configure_logger
from .version import __version__

LOGGER = structlog.getLogger(__name__)


def create_app() -> FastAPI:
    config_file = os.getenv("CONFIG_FILE", "./config/scanners.yml")
    if not config_file:
        raise ValueError("Config file is required")

    config = get_config(config_file)
    log_level = config.app.log_level
    is_debug = log_level == "DEBUG"
    configure_logger(log_level, config.app.log_json)

    configure_otel(config.app.name, config.tracing, config.metrics)

    vault = Vault()
    input_scanners_func = _get_input_scanners_function(config, vault)
    output_scanners_func = _get_output_scanners_function(config, vault)

    if config.app.scan_fail_fast:
        LOGGER.debug("Scan fail_fast mode is enabled")

    app = FastAPI(
        title=config.app.name,
        description="API to run LLM Guard scanners.",
        debug=is_debug,
        version=__version__,
        openapi_url="/openapi.json" if is_debug else None,  # hide docs in production
    )

    register_routes(app, config, input_scanners_func, output_scanners_func)

    instrument_app(app)

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
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Username or Password",
                )

        return True

    return check_auth


def _get_input_scanners_function(config: Config, vault: Vault) -> Callable:
    scanners = []
    if not config.app.lazy_load:
        LOGGER.debug("Loading input scanners")
        scanners = get_input_scanners(config.input_scanners, vault)

    def get_cached_scanners() -> List[InputScanner]:
        nonlocal scanners

        if not scanners and config.app.lazy_load:
            LOGGER.debug("Lazy loading input scanners")
            scanners = get_input_scanners(config.input_scanners, vault)

        return scanners

    return get_cached_scanners


def _get_output_scanners_function(config: Config, vault: Vault) -> Callable:
    scanners = []
    if not config.app.lazy_load:
        LOGGER.debug("Loading output scanners")
        scanners = get_output_scanners(config.output_scanners, vault)

    def get_cached_scanners() -> List[OutputScanner]:
        nonlocal scanners

        if not scanners and config.app.lazy_load:
            LOGGER.debug("Lazy loading output scanners")
            scanners = get_output_scanners(config.output_scanners, vault)

        return scanners

    return get_cached_scanners


def register_routes(
    app: FastAPI,
    config: Config,
    input_scanners_func: Callable,
    output_scanners_func: Callable,
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
    async def read_healthcheck():
        return JSONResponse({"status": "alive"})

    @app.get("/readyz", tags=["Health"])
    @limiter.exempt
    async def read_liveliness():
        return JSONResponse({"status": "ready"})

    @app.post(
        "/analyze/output",
        tags=["Analyze"],
        response_model=AnalyzeOutputResponse,
        status_code=status.HTTP_200_OK,
        description="Analyze an output and return the sanitized output and the results of the scanners",
    )
    async def submit_analyze_output(
        request: AnalyzeOutputRequest,
        _: Annotated[bool, Depends(check_auth)],
        output_scanners: List[OutputScanner] = Depends(output_scanners_func),
    ) -> AnalyzeOutputResponse:
        LOGGER.debug(
            "Received analyze output request",
            request_prompt=request.prompt,
            request_output=request.output,
        )

        if request.scanners_suppress is not None and len(request.scanners_suppress) > 0:
            LOGGER.debug("Suppressing scanners", scanners=request.scanners_suppress)
            output_scanners = [
                scanner
                for scanner in output_scanners
                if type(scanner).__name__ not in request.scanners_suppress
            ]

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

                for scanner, valid in results_valid.items():
                    scanners_valid_counter.add(
                        1, {"source": "output", "valid": valid, "scanner": scanner}
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
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Request timeout.",
                )

        return response

    @app.post(
        "/scan/output",
        tags=["Analyze"],
        response_model=ScanOutputResponse,
        status_code=status.HTTP_200_OK,
        description="Scans an output running scanners in parallel without sanitizing the prompt",
    )
    async def submit_scan_output(
        request: ScanOutputRequest,
        _: Annotated[bool, Depends(check_auth)],
        output_scanners: List[OutputScanner] = Depends(output_scanners_func),
    ) -> ScanOutputResponse:
        LOGGER.debug(
            "Received scan output request",
            request_prompt=request.prompt,
            request_output=request.output,
        )

        if request.scanners_suppress is not None and len(request.scanners_suppress) > 0:
            LOGGER.debug("Suppressing scanners", scanners=request.scanners_suppress)
            output_scanners = [
                scanner
                for scanner in output_scanners
                if type(scanner).__name__ not in request.scanners_suppress
            ]

        result_is_valid = True
        results_score = {}

        start_time = time.time()
        try:
            tasks = [
                ascan_output(scanner, request.prompt, request.output) for scanner in output_scanners
            ]
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=not config.app.scan_fail_fast),
                config.app.scan_output_timeout,
            )

            for result in results:
                if isinstance(result, InputIsInvalid):
                    result_is_valid = False
                    results_score[result.scanner_name] = result.risk_score

                    continue

                scanner_name, risk_score = result
                results_score[scanner_name] = risk_score
        except InputIsInvalid as e:
            result_is_valid = False
            results_score[e.scanner_name] = e.risk_score
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
            )

        response = ScanOutputResponse(
            is_valid=result_is_valid,
            scanners=results_score,
        )

        elapsed_time = time.time() - start_time
        LOGGER.debug(
            "Scan output response returned",
            scores=results_score,
            elapsed_time_seconds=round(elapsed_time, 6),
        )

        return response

    @app.post(
        "/analyze/prompt",
        tags=["Analyze"],
        response_model=AnalyzePromptResponse,
        status_code=status.HTTP_200_OK,
        description="Analyze a prompt and return the sanitized prompt and the results of the scanners",
    )
    async def submit_analyze_prompt(
        request: AnalyzePromptRequest,
        _: Annotated[bool, Depends(check_auth)],
        response: Response,
        input_scanners: List[InputScanner] = Depends(input_scanners_func),
    ) -> AnalyzePromptResponse:
        LOGGER.debug("Received analyze prompt request", request_prompt=request.prompt)

        if request.scanners_suppress is not None and len(request.scanners_suppress) > 0:
            LOGGER.debug("Suppressing scanners", scanners=request.scanners_suppress)
            input_scanners = [
                scanner
                for scanner in input_scanners
                if type(scanner).__name__ not in request.scanners_suppress
            ]

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

                for scanner, valid in results_valid.items():
                    scanners_valid_counter.add(
                        1, {"source": "input", "valid": valid, "scanner": scanner}
                    )

                response = AnalyzePromptResponse(
                    sanitized_prompt=sanitized_prompt,
                    is_valid=all(results_valid.values()),
                    scanners=results_score,
                )

                elapsed_time = time.time() - start_time
                LOGGER.debug(
                    "Sanitized prompt response returned",
                    scores=results_score,
                    elapsed_time_seconds=round(elapsed_time, 6),
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Request timeout.",
                )

        return response

    @app.post(
        "/scan/prompt",
        tags=["Analyze"],
        response_model=ScanPromptResponse,
        status_code=status.HTTP_200_OK,
        description="Scans a prompt running scanners in parallel without sanitizing the prompt",
    )
    async def submit_scan_prompt(
        request: ScanPromptRequest,
        _: Annotated[bool, Depends(check_auth)],
        input_scanners: List[InputScanner] = Depends(input_scanners_func),
    ) -> ScanPromptResponse:
        LOGGER.debug("Received scan prompt request", request_prompt=request.prompt)

        if request.scanners_suppress is not None and len(request.scanners_suppress) > 0:
            LOGGER.debug("Suppressing scanners", scanners=request.scanners_suppress)
            input_scanners = [
                scanner
                for scanner in input_scanners
                if type(scanner).__name__ not in request.scanners_suppress
            ]

        result_is_valid = True
        results_score = {}

        start_time = time.time()
        try:
            tasks = [ascan_prompt(scanner, request.prompt) for scanner in input_scanners]
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=not config.app.scan_fail_fast),
                config.app.scan_prompt_timeout,
            )

            for result in results:
                if isinstance(result, InputIsInvalid):
                    result_is_valid = False
                    results_score[result.scanner_name] = result.risk_score

                    continue

                scanner_name, risk_score = result
                results_score[scanner_name] = risk_score
        except InputIsInvalid as e:
            result_is_valid = False
            results_score[e.scanner_name] = e.risk_score
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
            )

        response = ScanPromptResponse(
            is_valid=result_is_valid,
            scanners=results_score,
        )

        elapsed_time = time.time() - start_time
        LOGGER.debug(
            "Scan prompt response returned",
            scores=results_score,
            elapsed_time_seconds=round(elapsed_time, 6),
        )

        return response

    if config.metrics and config.metrics.exporter == "prometheus":

        @app.get("/metrics", tags=["Metrics"])
        @limiter.exempt
        async def read_metrics():
            return Response(
                content=generate_latest(REGISTRY),
                headers={"Content-Type": CONTENT_TYPE_LATEST},
            )

    @app.on_event("shutdown")
    async def shutdown_event():
        LOGGER.info("Shutting down app...")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        LOGGER.warning(
            "HTTP exception",
            exception_status_code=exc.status_code,
            exception_detail=exc.detail,
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
