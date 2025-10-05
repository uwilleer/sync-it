from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from callbacks.main import MenuActionEnum, MenuCallback
from clients.schemas import SourceEnum
from clients.vacancy import vacancy_client
from commands import BotCommandEnum
from common.logger import get_logger
from database.models.enums import PreferencesCategoryCodeEnum
from keyboard.inline.main import main_keyboard
from schemas.user import UserRead
from utils.message import make_linked, safe_edit_message

from services import UserPreferenceService, UserService


__all__ = ["router"]

logger = get_logger(__name__)


router = Router(name=MenuCallback.__prefix__)


@router.message(Command(BotCommandEnum.START))
async def handle_start_command(
    message: Message, user: UserRead, user_preferences_service: UserPreferenceService, state: FSMContext
) -> None:
    await send_welcome_message(message, user, user_preferences_service, state)


@router.callback_query(MenuCallback.filter(F.action == MenuActionEnum.SHOW_MAIN))
async def handle_main_callback(
    callback: CallbackQuery,
    user_service: UserService,
    user_preferences_service: UserPreferenceService,
    state: FSMContext,
) -> None:
    user = await user_service.get_by_telegram_id(callback.from_user.id)

    await send_welcome_message(callback, user, user_preferences_service, state)


async def send_welcome_message(
    target: Message | CallbackQuery, user: UserRead, user_preferences_service: UserPreferenceService, state: FSMContext
) -> None:
    await state.clear()

    name = user.username or user.full_name
    linked_full_name = make_linked(name, user.username)

    summary = await vacancy_client.get_summary_vacancies()
    preferences = await user_preferences_service.get_by_user_id(user.id)

    enabled_sources = {
        pref.item_name for pref in preferences if pref.category_code == PreferencesCategoryCodeEnum.SOURCE
    }

    lines: list[str] = []
    for source in SourceEnum:
        count = summary.sources[source]
        normalized_source = SourceEnum(source.value)
        disabled_text = ""

        if enabled_sources and normalized_source.humanize() not in enabled_sources:
            disabled_text = " (выключено в предпочтениях)"

        lines.append(f"• {source.humanize()}: {count}{disabled_text}")

    sources_text = "\n".join(lines)

    text = (
        f"Привет, {linked_full_name} 👋\n\n"
        f"📊 В базе сейчас {summary.total} вакансий.\n"
        f"\t➕ За сутки добавлено: {summary.day_count}\n"
        f"\t➕ За неделю добавлено: {summary.week_count}\n"
        f"\t➕ За месяц добавлено: {summary.month_count}\n\n"
        f"🌍 Источники:\n"
        f"{sources_text}"
    )

    await safe_edit_message(
        target,
        text=text,
        reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
