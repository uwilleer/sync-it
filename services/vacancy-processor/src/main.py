from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from api import router as api_router
from api.v1 import router as v1_router
from common.environment.config import env_config
from common.sentry.initialize import init_sentry
from common.shared.api.exceptions import http_exception_custom_handler
from common.shared.api.middlewares import LoggingMiddleware
from fastapi import FastAPI, HTTPException
from seeds import seed_models
import uvicorn


@asynccontextmanager
async def lifespan(_fast_api: FastAPI) -> AsyncGenerator[None]:
    await seed_models()
    yield


app = FastAPI(
    title="Vacancy Processor Service",
    lifespan=lifespan,
    openapi_url="/openapi.json" if env_config.debug else None,
    docs_url="/docs" if env_config.debug else None,
    redoc_url="/redoc" if env_config.debug else None,
)

app.add_exception_handler(HTTPException, http_exception_custom_handler)

app.add_middleware(LoggingMiddleware)

app.include_router(api_router)
app.include_router(v1_router, prefix="/api/v1")


def main() -> None:
    init_sentry()

    uvicorn.run(
        "main:app",
        host=env_config.service_internal_host,
        port=env_config.service_internal_port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
