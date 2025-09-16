from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from callbacks.main import MenuActionEnum, MenuCallback
from clients.vacancy import vacancy_client
from commands import BotCommandEnum
from common.logger import get_logger
from keyboard.inline.main import main_keyboard
from keyboard.inline.preferences import preferences_keyboard
from schemas.user import UserRead
from utils.message import make_linked, safe_edit_message

from services import UserService


__all__ = ["router"]

logger = get_logger(__name__)


router = Router(name=MenuCallback.__prefix__)


@router.message(Command(BotCommandEnum.START))
async def handle_start_command(message: Message, user: UserRead, state: FSMContext) -> None:
    await send_welcome_message(message, user, state)


@router.callback_query(MenuCallback.filter(F.action == MenuActionEnum.MAIN))
async def handle_main_callback(callback: CallbackQuery, user_service: UserService, state: FSMContext) -> None:
    user = await user_service.get_by_telegram_id(callback.from_user.id)

    await send_welcome_message(callback, user, state)


@router.callback_query(MenuCallback.filter(F.action == MenuActionEnum.PREFERENCES))
async def handle_preferences(callback: CallbackQuery) -> None:
    await safe_edit_message(callback, text="⚙️ Выберите предпочтения:", reply_markup=preferences_keyboard())


async def send_welcome_message(target: Message | CallbackQuery, user: UserRead, state: FSMContext) -> None:
    await state.clear()

    linked_full_name = make_linked(user.full_name, user.username)

    summary = await vacancy_client.get_summary_vacancies()

    sources_text = "\n".join(f"• {source.humanize()}: {count}" for source, count in summary.sources.items())

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
