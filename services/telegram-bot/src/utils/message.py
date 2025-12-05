import asyncio
from typing import NotRequired, TypedDict, Unpack

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from common.logger import get_logger
from exceptions import MessageNotAvailableError, MessageNotModifiedError


logger = get_logger(__name__)


class EditMessageKwargs(TypedDict):
    text: NotRequired[str]
    parse_mode: NotRequired[ParseMode | None]
    reply_markup: NotRequired[InlineKeyboardMarkup | None]
    disable_web_page_preview: NotRequired[bool | None]


def make_linked(
    text: str, *, telegram_username: str | None = None, external_link: str | None = None, use_quotes: bool = True
) -> str:
    """Возвращает жирный текст, по возможности обёрнутый в ссылку."""

    bold_text = f"<b>{text}</b>"

    if telegram_username:
        return f'<a href="https://t.me/{telegram_username}">{bold_text}</a>'

    if external_link:
        return f'<a href="{external_link}">{bold_text}</a>'

    return f'"{bold_text}"' if use_quotes else bold_text


async def get_message(query: CallbackQuery | Message) -> Message:
    """Возвращает объект сообщения или выбрасывает исключение"""
    if isinstance(query, Message):
        return query
    if isinstance(query.message, Message):
        return query.message

    await query.answer("Произошла ошибка. Попробуйте позже.")

    raise MessageNotAvailableError


async def safe_edit_message(
    entity: CallbackQuery | Message,
    **kwargs: Unpack[EditMessageKwargs],
) -> None:
    """
    Безопасно редактирует сообщение.
    Если редактирование невозможно - отправляет новое.
    """
    message = await get_message(entity)

    # Заново отправляет сообщение, если оно было 'reply', чтобы 'reply' не висел во время работы
    if message.reply_to_message:
        try:
            await message.delete()
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.exception("Failed deleting message", exc_info=e)
        await message.answer(**kwargs)
        return

    try:
        await message.edit_text(**kwargs)
    except Exception as err:
        if isinstance(err, TelegramBadRequest) and "message is not modified" in err.message:
            raise MessageNotModifiedError from err

        try:
            await message.answer(**kwargs)
        except Exception as answer_err:
            logger.exception(
                "Failed to edit message and failed to answer as a fallback",
                exc_info=answer_err,
            )
