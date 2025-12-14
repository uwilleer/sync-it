import asyncio
import logging
from typing import Any

from g4f import Provider
from g4f.client import AsyncClient


logging.basicConfig(
    level=logging.DEBUG,  # уровень логирования
    format="%(message)s",  # формат вывода
    datefmt="%Y-%m-%d %H:%M:%S",  # формат времени
)
logger = logging.getLogger(__name__)

PROMPT = "Say OK"
MODEL = "gpt-4o-mini"
TIMEOUT = 5


async def test_provider(provider: Any) -> Any:
    client = AsyncClient(provider=provider)

    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": PROMPT}],
            ),
            timeout=TIMEOUT,
        )

        content = response.choices[0].message.content.strip()
        return provider.__name__, True, content  # noqa: TRY300

    except TimeoutError:
        return provider.__name__, False, "timeout"

    except Exception as e:  # noqa: BLE001
        return provider.__name__, False, str(e)


async def main() -> None:
    providers = [p for p in Provider.__dict__.values() if isinstance(p, type)]

    tasks = [test_provider(p) for p in providers]

    logger.info("\n=== RUNNING PROVIDER CHECK ===\n")

    for coro in asyncio.as_completed(tasks):
        name, ok, info = await coro

        if ok:
            logger.info(
                "%-5s %-30s %s",
                ok,
                name,
                info,
            )


if __name__ == "__main__":
    asyncio.run(main())
