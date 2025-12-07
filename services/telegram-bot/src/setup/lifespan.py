from commands import get_bot_commands
from core.loader import bot, dp
from handlers import register_handler_routers
from middlewares import register_middlewares


async def on_startup() -> None:
    register_handler_routers(dp)
    register_middlewares(dp)

    await bot.set_my_commands(get_bot_commands())


async def on_shutdown() -> None:
    await bot.delete_webhook()
    await bot.session.close()
