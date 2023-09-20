import logging
import os

import schemas
from cache import InMemoryCache
from config import load_scanners_from_config
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from llm_guard import scan_output, scan_prompt
from llm_guard.vault import Vault

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
is_debug = os.environ.get("DEBUG", True)
if is_debug:
    logger.setLevel(logging.DEBUG)

version = "0.0.1"


def create_app():
    cache = InMemoryCache(
        max_size=os.environ.get("CACHE_MAX_SIZE", None),
        expiration_time=os.environ.get("CACHE_TTL", 60 * 60),
    )

    vault = Vault()
    input_scanners, output_scanners = load_scanners_from_config(vault)

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
    def analyze_output(request: schemas.AnalyzeOutputRequest):
        logger.debug(f"Received analyze request: {request}")

        sanitized_output, results_valid, results_score = scan_output(
            output_scanners, request.prompt, request.output
        )
        response = schemas.AnalyzeOutputResponse(
            sanitized_output=sanitized_output,
            is_valid=all(results_valid.values()),
            scanners=results_score,
        )

        logger.debug(f"Sanitized response with the score: {results_score}")

        return response

    @app.post("/analyze/prompt", tags=["Analyze"])
    def analyze_prompt(request: schemas.AnalyzePromptRequest):
        logger.debug(f"Received analyze request: {request}")
        cached_result = cache.get(request.prompt)

        if cached_result:
            logger.debug("Response was found in cache")
            cached_result["is_cached"] = True

            return schemas.AnalyzePromptResponse(**cached_result)

        sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, request.prompt)
        response = schemas.AnalyzePromptResponse(
            sanitized_prompt=sanitized_prompt,
            is_valid=all(results_valid.values()),
            scanners=results_score,
        )

        cache.set(request.prompt, response.dict())

        logger.debug(f"Sanitized response with the score: {results_score}")

        return response

    @app.on_event("shutdown")
    def shutdown_event():
        logger.info({"message": "Shutting down app..."})

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        logger.warning(f"HTTP exception: {exc}. Request {request}")

        return JSONResponse(str(exc.detail), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.warning(f"Invalid request: {exc}. Request {request}")

        response = {"message": "Validation failed", "details": []}
        for error in exc.errors():
            response["details"].append(f"{'.'.join(error['loc'])}: {error['msg']}")

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
