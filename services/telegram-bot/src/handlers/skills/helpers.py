from pathlib import Path

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Document, Message
from common.logger import get_logger
from common.shared.clients.head_hunter import head_hunter_client
from core.loader import bot
from handlers.skills.schemas import FileResumePayloadSchema, ResumeError, TextResumePayloadSchema
from keyboard.inline.skills import update_skills_keyboard
from states import PreferencesState
from utils.common import extract_hh_resume_id
from utils.message import get_message, make_linked, safe_edit_message
from utils.readers.enums import SupportedReaderExtensionsEnum


logger = get_logger(__name__)


MAX_MESSAGE_LENGTH = 4096
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def get_update_preferences_text(*, text_to_insert: str | None = None, show_old_skills: bool = True) -> str:
    text = (
        "Пришлите информацию, где есть ваши навыки одним из способов:\n"
        f"— Ссылка на резюме в HeadHunter\n"
        f"— Файл в формате: {', '.join(SupportedReaderExtensionsEnum)} (до {MAX_FILE_SIZE // 1024 // 1024} МБ)\n"
        "— Текст (до 4096 символов)\n\n"
        f"ℹ️ Для лучшего результата можете использовать своё резюме.\n"
        f"ℹ️ Старайтесь избегать случаев, когда текст в файле представлен в виде картинок (например, png конвертирован в pdf), иначе точность извлечения навыков будет ниже.\n"  # noqa: E501
    )
    if text_to_insert:
        text += text_to_insert
    if show_old_skills:
        text += "⚠️ Обратите внимание: предыдущие навыки будут заменены новыми."

    return text


async def parse_resume_input(message: Message) -> FileResumePayloadSchema | TextResumePayloadSchema | ResumeError:
    if message.text:
        return await build_text_payload(message.text)

    if message.document:
        return await build_file_payload(message.document)

    return ResumeError(message="🤔 Вы прислали что-то непонятное.\n\n" + get_update_preferences_text())


async def build_file_payload(document: Document) -> FileResumePayloadSchema | ResumeError:
    file_suffix = Path(document.file_name or "").suffix
    if file_suffix not in SupportedReaderExtensionsEnum:
        return ResumeError(message=f"⚠️ Неподдерживаемый формат: {file_suffix}\n\n{get_update_preferences_text()}")

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        return ResumeError(message=f"⚠️ Файл должен быть меньше {MAX_FILE_SIZE // 1024 // 1024} МБ.")

    file = await bot.get_file(document.file_id)
    if not file.file_path:
        logger.error(
            "File path is not available for message: %s",
            document.model_dump(exclude_none=True),
        )
        return ResumeError(message=f"❌ Произошла ошибка. Попробуйте позже.\n\n{get_update_preferences_text()}")

    return FileResumePayloadSchema(file_path=file.file_path, suffix=file_suffix)


async def build_text_payload(text: str) -> TextResumePayloadSchema | ResumeError:
    if hh_resume_id := extract_hh_resume_id(text):
        resume_text = await head_hunter_client.get_resume_text(hh_resume_id)

        if not resume_text:
            guide = make_linked(
                "Как сделать резюме доступным по ссылке?",
                external_link="https://feedback.hh.ru/knowledge-base/article/1897",
            )
            return ResumeError(
                message=f"❌ Не удалось получить доступ к Вашему резюме.\n"
                f"Пожалуйста, убедитесь что резюме открыто для доступа по ссылке.\n\n{guide}"
            )

        return TextResumePayloadSchema(text=resume_text)

    # TODO: if is_linkedin_link

    if len(text) > MAX_MESSAGE_LENGTH:
        return ResumeError(
            message=f"⚠️ Текст слишком длинный, попробуйте сократить его.\n\n{get_update_preferences_text()}"
        )

    return TextResumePayloadSchema(text=text)


async def update_skills(
    entity: CallbackQuery | Message, state: FSMContext, *, need_edit: bool = True, is_first_start: bool = False
) -> None:
    if need_edit:
        await safe_edit_message(
            entity,
            text=get_update_preferences_text(),
            reply_markup=update_skills_keyboard(),
        )
    else:
        text_to_insert = (
            "ℹ️ Если нет возможности присылать резюме — просто перечислите хотя бы несколько основных навыков, "
            "фреймворков или библиотек (например: <code>Python, FastAPI, aiogram, React, Docker</code>), "
            "далее Вы сможете быстро добавлять навыки в кнопках под вакансиями."
        )
        text = get_update_preferences_text(
            text_to_insert=text_to_insert if is_first_start else None,
            show_old_skills=not is_first_start,
        )
        message = await get_message(entity)
        await message.answer(text, reply_markup=update_skills_keyboard(), parse_mode=ParseMode.HTML)

    await state.set_state(PreferencesState.waiting_for_data)
