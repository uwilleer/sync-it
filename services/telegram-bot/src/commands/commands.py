from aiogram.types import BotCommand
from commands.enums import CommandEnum


__all__ = [
    "BotCommandEnum",
    "get_bot_commands",
]


class BotCommandEnum(CommandEnum):
    START = "start", "Запустить бота"
    FAQ = "faq", "FAQ"
    UPDATE_SKILLS = "update_skills", "Обновить навыки на основе текста или файла"
    SUPPORT = "support", "Обратная связь"


def get_bot_commands() -> list[BotCommand]:
    return [BotCommand(command=cmd, description=cmd.description) for cmd in BotCommandEnum]
