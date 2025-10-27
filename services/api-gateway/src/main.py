from clients import proxy_client
from common.environment.config import env_config
from common.gateway.config import gateway_config
from common.gateway.enums import ServiceEnum
from common.logger import get_logger
from common.sentry.initialize import init_sentry
from common.shared.api.exceptions import http_exception_custom_handler
from common.shared.api.middlewares import LoggingMiddleware
from dependencies import validate_api_key
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from schemas import HealthResponse
import uvicorn


logger = get_logger(__name__)


app = FastAPI(
    title="API Gateway Service",
    openapi_url="/openapi.json" if env_config.debug else None,
    docs_url="/docs" if env_config.debug else None,
    redoc_url="/redoc" if env_config.debug else None,
)

app.add_exception_handler(HTTPException, http_exception_custom_handler)

app.add_middleware(LoggingMiddleware)


@app.get("/{service}/{path:path}", dependencies=[Depends(validate_api_key)])
async def get_gateway_proxy(service: ServiceEnum, path: str, request: Request) -> Response:
    return await proxy_client.proxy_request(service, path, request)


@app.post("/{service}/{path:path}", dependencies=[Depends(validate_api_key)])
async def post_gateway_proxy(service: ServiceEnum, path: str, request: Request) -> Response:
    return await proxy_client.proxy_request(service, path, request)


@app.delete("/{service}/{path:path}", dependencies=[Depends(validate_api_key)])
async def delete_gateway_proxy(service: ServiceEnum, path: str, request: Request) -> Response:
    return await proxy_client.proxy_request(service, path, request)


@app.get("/health")
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="Healthy")


def main() -> None:
    init_sentry()

    uvicorn.run(
        "main:app",
        host=gateway_config.host,
        port=gateway_config.port,
        log_config=None,
    )


if __name__ == "__main__":
    main()
