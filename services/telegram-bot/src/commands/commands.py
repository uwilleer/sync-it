from aiogram.types import BotCommand
from commands.enums import CommandEnum


__all__ = [
    "BotCommandEnum",
    "get_bot_commands",
]


class BotCommandEnum(CommandEnum):
    START = "start", "Перезапустить бота"
    UPDATE_SKILLS = "update_skills", "Обновить навыки на основе текста или файла"
    FAQ = "faq", "FAQ"
    SUPPORT = "support", "Обратная связь"


def get_bot_commands() -> list[BotCommand]:
    return [BotCommand(command=cmd, description=cmd.description) for cmd in BotCommandEnum]
