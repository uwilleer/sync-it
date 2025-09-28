from api import router as api_router
from api.v1 import router as v1_router
from common.environment.config import env_config
from common.logger import get_logger
from common.logger.config import log_config
from common.sentry.initialize import init_sentry
from fastapi import FastAPI
import uvicorn


logger = get_logger(__name__)

app = FastAPI(title="Scraper API Service")

app.include_router(api_router)
app.include_router(v1_router, prefix="/api/v1")


def main() -> None:
    init_sentry()

    uvicorn.run(
        "main:app",
        host=env_config.service_internal_host,
        port=env_config.service_internal_port,
        log_level=log_config.level.lower(),
    )


if __name__ == "__main__":
    main()
