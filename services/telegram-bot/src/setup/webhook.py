from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from aiogram.types import Update
from common.environment.config import env_config
from common.logger.config import log_config
from core import service_config
from core.loader import bot, dp
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from setup.lifespan import on_shutdown, on_startup
from starlette import status
from starlette.requests import Request
import uvicorn


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)


class WebhookResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str


@app.post("/webhook")
async def bot_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> WebhookResponse:
    if service_config.webhook_api_key != x_telegram_bot_api_secret_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret token")

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_webhook_update(bot=bot, update=update)

    return WebhookResponse(status="ok")


@app.get("/health")
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="Healthy")


async def start_webhook() -> None:
    await bot.set_webhook(
        url=str(service_config.webhook_url),
        drop_pending_updates=True,
        secret_token=service_config.webhook_api_key,
    )

    config = uvicorn.Config(
        "setup.webhook:app",
        host=env_config.service_internal_host,
        port=env_config.service_internal_port,
        log_level=log_config.level.lower(),
    )

    server = uvicorn.Server(config=config)
    await server.serve()
