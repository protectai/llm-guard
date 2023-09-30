import asyncio
import concurrent.futures
import logging
import time

import schemas
from cache import InMemoryCache
from config import get_env_config, load_scanners_from_config
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from llm_guard import scan_output, scan_prompt
from llm_guard.vault import Vault

config = get_env_config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
is_debug = config["debug"]
if is_debug:
    logger.setLevel(logging.DEBUG)

version = "0.0.2"


def create_app():
    cache = InMemoryCache(
        max_size=config["cache_ttl"],
        expiration_time=config["cache_ttl"],
    )

    vault = Vault()
    input_scanners, output_scanners = load_scanners_from_config(vault)

    if config["scan_fail_fast"] == True:
        logger.debug("Scan fail fast is enabled")

    app = FastAPI(
        title="LLM Guard API",
        description="API to run LLM Guard scanners",
        debug=is_debug,
        version=version,
        openapi_url="/openapi.json" if is_debug else None,  # hide docs in production
    )

    register_middlewares(app)

    register_routes(app, cache, input_scanners, output_scanners)

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
        request: schemas.AnalyzeOutputRequest,
    ) -> schemas.AnalyzeOutputResponse:
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
                        config["scan_fail_fast"],
                    ),
                    timeout=config["scan_output_timeout"],
                )

                response = schemas.AnalyzeOutputResponse(
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
        request: schemas.AnalyzePromptRequest,
    ) -> schemas.AnalyzePromptResponse:
        logger.debug(f"Received analyze request: {request}")
        cached_result = cache.get(request.prompt)

        if cached_result:
            logger.debug("Response was found in cache")
            cached_result["is_cached"] = True

            return schemas.AnalyzePromptResponse(**cached_result)

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
                        config["scan_fail_fast"],
                    ),
                    timeout=config["scan_prompt_timeout"],
                )

                response = schemas.AnalyzePromptResponse(
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        server_header=False,
    )
