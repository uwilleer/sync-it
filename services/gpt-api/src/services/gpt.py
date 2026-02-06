import asyncio

from aiohttp import ClientResponseError
from common.logger import get_logger
from common.shared.decorators.concurency import limit_requests
from core.config import service_config
from google import genai


logger = get_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 3

client = genai.Client(api_key=service_config.gemini_api_key.get_secret_value())


@limit_requests(128)
async def get_gpt_response(prompt: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=service_config.gemini_model,
                contents=prompt,
            )
        except ClientResponseError as e:
            logger.exception("Failed to get GPT response on attempt %s", attempt, exc_info=e)
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(RETRY_DELAY)
        else:
            return response.text

    return None
