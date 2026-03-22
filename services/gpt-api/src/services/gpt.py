import asyncio

from common.logger import get_logger
from common.shared.clients import http_client
from common.shared.clients import limits as http_limits
from common.shared.decorators.concurency import limit_requests
from core.config import service_config
import httpx
from openai import AsyncOpenAI


logger = get_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 3

http_client = (
    httpx.AsyncClient(limits=http_limits, proxy=service_config.openai_proxy)
    if service_config.openai_proxy
    else http_client
)

client = AsyncOpenAI(
    api_key=service_config.openai_api_key.get_secret_value(),
    http_client=http_client,
)


@limit_requests(64)
async def get_gpt_response(prompt: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=service_config.openai_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.exception("Failed to get GPT response on attempt %s", attempt, exc_info=e)
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(RETRY_DELAY)

    return None
