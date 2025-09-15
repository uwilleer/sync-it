import asyncio
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
from keyboard.inline.main import main_menu_keyboard
from keyboard.inline.skills import show_skills_keyboard, update_skills_keyboard
from schemas.user import UserRead
from states import PreferencesState
from tasks import process_resume
from tasks.schemas import FileResumePayloadSchema, TextResumePayloadSchema
from utils.message import get_message, safe_edit_message
from utils.readers.enums import SupportedReaderExtensionsEnum

from services import UserPreferenceService


__all__ = ["update_skills"]

logger = get_logger(__name__)


router = Router(name=SkillCallback.__prefix__)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_MESSAGE_LENGTH = 4096


update_preferences_text = (
    "Пришлите информацию, где есть Ваши навыки одним из способов:\n"
    "— Текстом (до 4096 символов)\n"
    f"— Файлом в формате: {', '.join(SupportedReaderExtensionsEnum)} (до {MAX_FILE_SIZE // 1024 // 1024} МБ)\n\n"
    f"ℹ️ Все ваши прошлые навыки будут удалены.\n"
    f"ℹ️ Для более точного поиска вакансий, пришлите Ваше резюме.\n"
    f"ℹ️ Старайтесь избегать случаев, когда текст в файле представлен в виде картинок (например, конвертация png в pdf), иначе точность извлечения навыков будет ниже."  # noqa: E501
)


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
    if not preferences:
        await safe_edit_message(callback, text="У вас пока нет добавленных навыков. \nПожалуйста, добавьте их.")
        await asyncio.sleep(1)
        await update_skills(callback, state, need_edit=False)
        return

    sorted_preferences = sorted(preferences, key=lambda p: p.item_name.casefold())
    preferences_str = ", ".join(f"<code>{p.item_name}</code>" for p in sorted_preferences)

    await state.set_state(PreferencesState.waiting_toggle_skills)
    await safe_edit_message(
        callback,
        text=(
            "📚 <b>Ваши навыки</b>:\n"
            f"{preferences_str}\n\n"
            "✅ Чтобы <b>добавить</b> новый навык — просто отправьте его название.\n"
            "❌ Чтобы <b>удалить</b> навык — отправьте его название из списка."
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
                f"⚠️ Текст слишком длинный, попробуйте сократить его.\n\n{update_preferences_text}",
                reply_markup=main_menu_keyboard(),
            )
            return
        resume_payload = TextResumePayloadSchema(text=text)
    elif document := message.document:
        file_suffix = Path(document.file_name or "").suffix
        if not file_suffix:
            await message.reply(
                f"⚠️ Не удалось определить формат файла.\n\n{update_preferences_text}",
                reply_markup=main_menu_keyboard(),
            )
            return

        if file_suffix not in SupportedReaderExtensionsEnum:
            await message.reply(
                f"⚠️ Неподдерживаемый формат: {file_suffix}\n\n{update_preferences_text}",
                reply_markup=main_menu_keyboard(),
            )
            return

        if not document.file_size:
            logger.warning(
                "File size is not available for message: %s",
                message.model_dump(exclude_none=True),
            )
            await message.reply(
                f"❌ Произошла ошибка. Попробуйте позже.\n\n{update_preferences_text}",
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
                f"❌ Произошла ошибка. Попробуйте позже.\n\n{update_preferences_text}",
                reply_markup=main_menu_keyboard(),
            )
            return

        resume_payload = FileResumePayloadSchema(file_path=file.file_path, suffix=file_suffix)
    else:
        await message.reply(
            f"🤔 Вы прислали что-то не понятное.\n\n{update_preferences_text}",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        "ℹ️ Начинаю извлечение навыков из текста.\nПожалуйста, подождите, это может занять некоторое время.",
    )

    process_resume.delay(user.id, message.chat.id, resume_payload.model_dump(), toggle=need_toggle)
    await state.clear()


async def update_skills(entity: CallbackQuery | Message, state: FSMContext, *, need_edit: bool = True) -> None:
    if need_edit:
        await safe_edit_message(
            entity,
            text=update_preferences_text,
            reply_markup=update_skills_keyboard(),
        )
    else:
        message = await get_message(entity)
        await message.answer(update_preferences_text, reply_markup=update_skills_keyboard())

    await state.set_state(PreferencesState.waiting_for_data)
