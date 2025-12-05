from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from callbacks.skill import SkillActionEnum, SkillCallback
from database.models.enums import PreferencesCategoryCodeEnum
from keyboard.inline.buttons import ImportSkillsInlineKeyboardButton
from keyboard.inline.skills import show_skills_keyboard
from states import PreferencesState
from utils.message import safe_edit_message

from services import UserPreferenceService


router = Router()


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
