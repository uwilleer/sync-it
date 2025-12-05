from common.environment.config import env_config
from common.logger import get_logger
from common.sentry.initialize import init_sentry
from core import service_config
from setup import start_polling, start_webhook
import uvloop


__all__ = ()


logger = get_logger(__name__)


async def main() -> None:
    init_sentry()

    if service_config.use_webhook:
        await start_webhook()
    else:
        await start_polling()


if __name__ == "__main__":
    uvloop.run(main(), debug=env_config.debug)
