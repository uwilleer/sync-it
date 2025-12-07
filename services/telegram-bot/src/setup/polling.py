from common.environment.config import env_config
from common.logger import get_logger
from core.loader import bot, dp
from setup.lifespan import on_shutdown, on_startup


logger = get_logger(__name__)


async def start_polling() -> None:
    logger.info("Start polling")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if not env_config.debug:  # Нужно ждать запуска бота, чтобы отправлять команды
        await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)
