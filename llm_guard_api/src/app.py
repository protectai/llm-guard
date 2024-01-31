import asyncio
import concurrent.futures
import logging
import os
import time

from cache import InMemoryCache
from config import get_config
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas import (
    AnalyzeOutputRequest,
    AnalyzeOutputResponse,
    AnalyzePromptRequest,
    AnalyzePromptResponse,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from llm_guard import scan_output, scan_prompt
from llm_guard.vault import Vault

version = "0.0.5"

logger = logging.getLogger("llm-guard-api")

vault = Vault()
scanners_config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config",
    "scanners.yml",
)

config = get_config(vault, scanners_config_file)
logger.setLevel(logging.INFO)
is_debug = config["app"]["debug"]
if is_debug:
    logger.setLevel(logging.DEBUG)


def create_app():
    cache = InMemoryCache(
        max_size=int(config["app"]["cache_ttl"]),
        expiration_time=int(config["app"]["cache_ttl"]),
    )

    if config["app"]["scan_fail_fast"]:
        logger.debug("Scan fail_fast mode is enabled")

    app = FastAPI(
        title=config["app"]["name"],
        description="API to run LLM Guard scanners.",
        debug=is_debug,
        version=version,
        openapi_url="/openapi.json" if is_debug else None,  # hide docs in production
    )

    register_middlewares(app)

    register_routes(app, cache, config["input_scanners"], config["output_scanners"])

    return app


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type"],
    )


def register_routes(
    app: FastAPI, cache: InMemoryCache, input_scanners: list, output_scanners: list
):
    @app.get("/", tags=["Main"])
    async def read_root():
        return {"name": "LLM Guard API"}

    @app.get("/healthz", tags=["Health"])
    async def healthcheck():
        return JSONResponse({"status": "alive"})

    @app.get("/readyz", tags=["Health"])
    async def liveliness():
        return JSONResponse({"status": "ready"})

    @app.post("/analyze/output", tags=["Analyze"])
    async def analyze_output(
        request: AnalyzeOutputRequest,
    ) -> AnalyzeOutputResponse:
        logger.debug(f"Received analyze request: {request}")

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
                        config["app"]["scan_fail_fast"],
                    ),
                    timeout=float(config["app"]["scan_output_timeout"]),
                )

                response = AnalyzeOutputResponse(
                    sanitized_output=sanitized_output,
                    is_valid=all(results_valid.values()),
                    scanners=results_score,
                )
                elapsed_time = time.time() - start_time
                logger.debug(
                    f"Sanitized response with the score: {results_score}. Elapsed time: {elapsed_time:.6f} seconds"
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
                )

        return response

    @app.post("/analyze/prompt", tags=["Analyze"])
    async def analyze_prompt(
        request: AnalyzePromptRequest,
    ) -> AnalyzePromptResponse:
        logger.debug(f"Received analyze request: {request}")
        cached_result = cache.get(request.prompt)

        if cached_result:
            logger.debug("Response was found in cache")
            cached_result["is_cached"] = True

            return AnalyzePromptResponse(**cached_result)

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
                        config["app"]["scan_fail_fast"],
                    ),
                    timeout=float(config["app"]["scan_prompt_timeout"]),
                )

                response = AnalyzePromptResponse(
                    sanitized_prompt=sanitized_prompt,
                    is_valid=all(results_valid.values()),
                    scanners=results_score,
                )
                cache.set(request.prompt, response.dict())

                elapsed_time = time.time() - start_time
                logger.debug(
                    f"Sanitized response with the score: {results_score}. Elapsed time: {elapsed_time:.6f} seconds"
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout."
                )

        return response

    @app.on_event("shutdown")
    def shutdown_event():
        logger.info({"message": "Shutting down app..."})

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        logger.warning(f"HTTP exception: {exc}. Request {request}")

        return JSONResponse(
            {"message": str(exc.detail), "details": None}, status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.warning(f"Invalid request: {exc}. Request {request}")

        response = {"message": "Validation failed", "details": exc.errors()}
        return JSONResponse(
            jsonable_encoder(response), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


app = create_app()
