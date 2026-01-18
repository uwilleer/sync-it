import asyncio

from common.logger import get_logger
from common.shared.decorators.concurency import limit_requests
from core.settings import service_config
from openai import AsyncOpenAI


logger = get_logger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 3

base_url = "https://api.groq.com/openai/v1"

client = AsyncOpenAI(
    api_key=service_config.groq_api_key,
    base_url=base_url,
)


@limit_requests(16)
async def get_gpt_response(prompt: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=service_config.groq_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.exception("Failed to get GPT response on attempt %s", attempt, exc_info=e)
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(RETRY_DELAY)

    return None
