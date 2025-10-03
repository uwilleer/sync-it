from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from callbacks.skill import SkillActionEnum, SkillCallback
from commands import BotCommandEnum
from common.logger import get_logger
from core.loader import bot
from database.models.enums import PreferencesCategoryCodeEnum
from keyboard.inline.buttons import ImportSkillsInlineKeyboardButton
from keyboard.inline.main import main_menu_keyboard
from keyboard.inline.skills import show_skills_keyboard, update_skills_keyboard
from schemas.user import UserRead
from states import PreferencesState
from tasks import process_resume
from tasks.enums import ResumeTypeEnum
from tasks.schemas import FileResumePayloadSchema, TextResumePayloadSchema
from utils.message import get_message, safe_edit_message
from utils.readers.enums import SupportedReaderExtensionsEnum

from services import UserPreferenceService


__all__ = ["update_skills"]

logger = get_logger(__name__)


router = Router(name=SkillCallback.__prefix__)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_MESSAGE_LENGTH = 4096


def get_update_preferences_text(*, text_to_insert: str | None = None, show_old_skills: bool = True) -> str:
    text = (
        "Пришлите информацию, где есть ваши навыки одним из способов:\n"
        "— Текстом (до 4096 символов)\n"
        f"— Файлом в формате: {', '.join(SupportedReaderExtensionsEnum)} (до {MAX_FILE_SIZE // 1024 // 1024} МБ)\n\n"
        f"ℹ️ Для лучшего результата можете использовать своё резюме.\n"
        f"ℹ️ Старайтесь избегать случаев, когда текст в файле представлен в виде картинок (например, конвертация png в pdf), иначе точность извлечения навыков будет ниже.\n"  # noqa: E501
    )
    if text_to_insert:
        text += text_to_insert
    if show_old_skills:
        text += "⚠️ Обратите внимание: предыдущие навыки будут заменены новыми."

    return text


@router.message(Command(BotCommandEnum.UPDATE_SKILLS))
async def handle_update_skills_command(message: Message, state: FSMContext) -> None:
    await update_skills(message, state)


@router.callback_query(SkillCallback.filter(F.action == SkillActionEnum.UPDATE_SKILLS))
async def handle_update_skills_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await update_skills(callback, state)


@router.callback_query(SkillCallback.filter(F.action == SkillActionEnum.TOGGLE_SKILLS))
async def handle_toggle_skills(
    callback: CallbackQuery, user_preferences_service: UserPreferenceService, state: FSMContext
) -> None:
    preferences = await user_preferences_service.filter_by_telegram_id_and_category(
        callback.from_user.id, PreferencesCategoryCodeEnum.SKILL
    )
    sorted_preferences = sorted(preferences, key=lambda p: p.item_name.casefold())
    preferences_str = ", ".join(f"<code>{p.item_name}</code>" for p in sorted_preferences)

    prefix = "📚 <b>Ваши навыки</b>:\n" if preferences_str else "😕 <b>У вас пока нет навыков</b>."

    await state.set_state(PreferencesState.waiting_toggle_skills)
    await safe_edit_message(
        callback,
        text=(
            f"{prefix}"
            f"{preferences_str}\n\n"
            f"✅ Чтобы <b>добавить</b> новый навык — просто отправьте его название "
            f'или воспользуйтесь кнопкой "<b>{ImportSkillsInlineKeyboardButton().text}</b>"\n'
            "❌ Чтобы <b>удалить</b> навык — отправьте его название из списка.\n"
            "ℹ️ Если хотите добавить/удалить несколько навыков — перечислите их через запятую."
        ),
        reply_markup=show_skills_keyboard(),
        parse_mode=ParseMode.HTML,
    )


@router.message(StateFilter(PreferencesState.waiting_for_data, PreferencesState.waiting_toggle_skills))
async def handle_resume_input(message: Message, state: FSMContext, user: UserRead) -> None:  # noqa: PLR0911
    resume_payload: TextResumePayloadSchema | FileResumePayloadSchema
    need_toggle = await state.get_state() == PreferencesState.waiting_toggle_skills

    if text := message.text:
        if len(text) > MAX_MESSAGE_LENGTH:
            await message.reply(
                f"⚠️ Текст слишком длинный, попробуйте сократить его.\n\n{get_update_preferences_text()}",
                reply_markup=main_menu_keyboard(),
            )
            return
        resume_payload = TextResumePayloadSchema(text=text)
    elif document := message.document:
        file_suffix = Path(document.file_name or "").suffix
        if not file_suffix:
            await message.reply(
                f"⚠️ Не удалось определить формат файла.\n\n{get_update_preferences_text()}",
                reply_markup=main_menu_keyboard(),
            )
            return

        if file_suffix not in SupportedReaderExtensionsEnum:
            await message.reply(
                f"⚠️ Неподдерживаемый формат: {file_suffix}\n\n{get_update_preferences_text()}",
                reply_markup=main_menu_keyboard(),
            )
            return

        if not document.file_size:
            logger.warning(
                "File size is not available for message: %s",
                message.model_dump(exclude_none=True),
            )
            await message.reply(
                f"❌ Произошла ошибка. Попробуйте позже.\n\n{get_update_preferences_text()}",
                reply_markup=main_menu_keyboard(),
            )
            return

        if document.file_size > MAX_FILE_SIZE:
            await message.reply(
                f"⚠️ Файл должен быть меньше {MAX_FILE_SIZE // 1024 // 1024} МБ.",
                reply_markup=main_menu_keyboard(),
            )
            return

        file = await bot.get_file(document.file_id)
        if not file.file_path:
            logger.warning(
                "File path is not available for message: %s",
                message.model_dump(exclude_none=True),
            )
            await message.reply(
                f"❌ Произошла ошибка. Попробуйте позже.\n\n{get_update_preferences_text()}",
                reply_markup=main_menu_keyboard(),
            )
            return

        resume_payload = FileResumePayloadSchema(file_path=file.file_path, suffix=file_suffix)
    else:
        await message.reply(
            f"🤔 Вы прислали что-то не понятное.\n\n{get_update_preferences_text()}",
            reply_markup=main_menu_keyboard(),
        )
        return

    file_type_text = "файла" if resume_payload.type == ResumeTypeEnum.FILE else "текста"
    await message.answer(
        f"ℹ️ Начинаю извлечение навыков из {file_type_text}.\nПожалуйста, подождите, это может занять некоторое время.",
    )

    process_resume.delay(user.id, message.chat.id, resume_payload.model_dump(), toggle=need_toggle)
    await state.clear()


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
            "ℹ️ Если не хотите присылать резюме — просто перечислите хотя бы несколько навыков, "
            "фреймворков или библиотек "
            "(например: <code>Python, FastAPI, aiogram, React, Docker</code>), "
            "иначе я не смогу подобрать для вас вакансии"
        )
        text = get_update_preferences_text(
            text_to_insert=text_to_insert if is_first_start else None,
            show_old_skills=not is_first_start,
        )
        message = await get_message(entity)
        await message.answer(text, reply_markup=update_skills_keyboard(), parse_mode=ParseMode.HTML)

    await state.set_state(PreferencesState.waiting_for_data)
