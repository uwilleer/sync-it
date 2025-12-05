from aiogram.filters import Command
from aiogram.types import Message
from commands import BotCommandEnum
from handlers.faq import router
from handlers.faq.helpers import send_faq_message


@router.message(Command(BotCommandEnum.FAQ))
async def handle_faq_command(message: Message) -> None:
    await send_faq_message(message)
