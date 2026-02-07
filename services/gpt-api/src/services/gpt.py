import asyncio

from aiohttp import ClientResponseError
from common.logger import get_logger
from common.shared.decorators.concurency import limit_requests
from core.config import service_config
from google import genai


logger = get_logger(__name__)

MODELS = (
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview",
    "models/gemini-pro-latest",
    "models/gemini-2.5-pro",
    "models/gemini-2.5-flash",
    "models/gemma-3-27b-it",
    "models/gemma-3-12b-it",
    "models/gemma-3-4b-it",
)

MAX_RETRIES = len(MODELS)
RETRY_DELAY = 3

client = genai.Client(api_key=service_config.gemini_api_key.get_secret_value())


@limit_requests(16)
async def get_gpt_response(prompt: str) -> str | None:
    for attempt, model in enumerate(MODELS, start=1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
        except ClientResponseError as e:
            logger.exception("Failed to get GPT response on attempt %s", attempt, exc_info=e)
            if attempt > MAX_RETRIES:
                return None
            await asyncio.sleep(RETRY_DELAY)
        else:
            return response.text

    return None
