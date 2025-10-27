import time

from common.logger import get_logger
from common.sentry.config import sentry_config
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


__all__ = ["LoggingMiddleware"]


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Логирование информации о запросе сервиса с FastAPI"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # noqa: PLR6301
        start_time = time.time()

        client = request.client
        client_ip = "Unknown" if not client else client.host

        method = request.method
        url = request.url.path

        logger.info("Request: %s %s from %s", method, url, client_ip)

        response = await call_next(request)

        status = response.status_code
        process_time_seconds = time.time() - start_time
        process_time_ms = process_time_seconds * 1000

        if process_time_seconds > sentry_config.slow_api_threshold:
            logger.warning(
                "Slow API request: %s %s from %s status=%s time=%0.2fms",
                method,
                url,
                client_ip,
                status,
                process_time_ms,
                extra={"duration": process_time_ms},
            )

        logger.info("Response: %s %s status=%s from %s time=%0.2fms", method, url, status, client_ip, process_time_ms)

        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

        return response
