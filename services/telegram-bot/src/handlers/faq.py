from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from commands import BotCommandEnum
from core import service_config
from keyboard.inline.main import main_menu_keyboard
from keyboard.reply.general import general_keyboard
from utils.message import make_linked


__all__ = ["router"]


router = Router(name=BotCommandEnum.FAQ)


@router.message(Command(BotCommandEnum.FAQ))
async def handle_faq_command(message: Message) -> None:
    await send_faq_message(message)


async def send_faq_message(message: Message, *, is_first_start: bool = False) -> None:
    text = FAQ_TEXT
    if is_first_start:
        text += f"\n\n💬 Нужна помощь? Пишите в поддержку: @{service_config.support_username}"

    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=general_keyboard() if is_first_start else main_menu_keyboard(),
    )


FAQ_TEXT = f"""
❓ <b>FAQ</b>

📢 <b>Наш канал в Telegram</b>
Не пропусти важное! Подписывайся на {make_linked("syncIT Hub", "syncit_hub")},
чтобы всегда быть в курсе новостей, новых фич и эксклюзивных обновлений нашего сервиса.

🤖 <b>Что это за сервис?</b>
<b>syncIT</b> — ваш персональный помощник по поиску работы в IT.
Бот анализирует ваши профессиональные навыки и предпочтения, автоматически подбирая наиболее релевантные вакансии из различных источников.

🎯 <b>Как работает подбор вакансий?</b>
1. <i>Агрегация</i>: вакансии собираются из различных платформ
2. <i>Анализ</i>: из каждой вакансии извлекается ключевая информация: профессия, грейд, формат работы, зарплата, требования и условия работы
3. <i>Подбор</i>: вы получаете только те вакансии, которые могут быть вам интересны
"""  # noqa: E501
