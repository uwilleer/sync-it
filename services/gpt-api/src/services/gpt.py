from typing import cast

from common.logger import get_logger
from common.shared.clients import http_client
from common.shared.decorators.concurency import limit_requests


__all__ = ["get_gpt_response"]


logger = get_logger(__name__)


@limit_requests(100)
async def get_gpt_response(prompt: str) -> str | None:
    url = "https://api.laozhang.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-x44C9oPPWHGWmT4c51D07816Ee3d4eCdA642D9D2E8904b82",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "stream": False,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = await http_client.post(url, headers=headers, json=data)
        response.raise_for_status()
        data = response.json()

        return cast("str", data["choices"][0]["message"]["content"])
    except Exception as e:
        logger.exception("Failed to get GPT completion", exc_info=e)

    return None
