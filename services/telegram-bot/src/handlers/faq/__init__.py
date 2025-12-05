from aiogram import Router
from commands import BotCommandEnum


router = Router(name=BotCommandEnum.FAQ)

__all__ = ["router"]
