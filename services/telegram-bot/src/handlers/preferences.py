from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from callbacks.main import MenuActionEnum, MenuCallback
from callbacks.preferences import PreferencesActionEnum, PreferencesCallback
from clients import grade_client, profession_client, work_format_client
from clients.vacancy import vacancy_client
from common.logger import get_logger
from database.models.enums import PreferencesCategoryCodeEnum
from keyboard.inline.preferences import options_keyboard, preferences_keyboard
from keyboard.reply.buttons import PreferencesChangeKeyboardButton
from schemas.user import UserRead
from schemas.user_preference import UserPreferenceCreate
from services.user import UserService
from unitofwork import UnitOfWork
from utils.clients import get_client
from utils.message import get_message, safe_edit_message

from services import UserPreferenceService


logger = get_logger(__name__)


router = Router(name=PreferencesCallback.__prefix__)


@router.callback_query(MenuCallback.filter(F.action == MenuActionEnum.SHOW_PREFERENCES))
async def handle_preferences(callback: CallbackQuery) -> None:
    await safe_edit_message(callback, text="⚙️ Выберите предпочтения:", reply_markup=preferences_keyboard())


@router.message(F.text == PreferencesChangeKeyboardButton().text)
async def handle_preferences_message(message: Message) -> None:
    await safe_edit_message(message, text="⚙️ Выберите предпочтения:", reply_markup=preferences_keyboard())


async def handle_show_options(
    query: CallbackQuery,
    user_service: UserService,
    category_code: PreferencesCategoryCodeEnum,
    client_method: Callable[..., Awaitable[Any]],
    message_text: str,
) -> None:
    options = await client_method()

    user = await user_service.get_by_telegram_id(query.from_user.id, with_preferences=True)

    await safe_edit_message(
        query,
        text=message_text,
        reply_markup=options_keyboard(category_code, options, user),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(PreferencesCallback.filter(F.action == PreferencesActionEnum.SHOW_PROFESSIONS))
async def handle_profession(query: CallbackQuery, user_service: UserService) -> None:
    await handle_show_options(
        query,
        user_service,
        PreferencesCategoryCodeEnum.PROFESSION,
        profession_client.get_all,
        "Выберите профессию.\n\nℹ️ <i>Неизвестно — вакансии, у которых не удалось определить профессию.</i>",
    )


@router.callback_query(PreferencesCallback.filter(F.action == PreferencesActionEnum.SHOW_WORK_FORMATS))
async def handle_work_format(query: CallbackQuery, user_service: UserService) -> None:
    await handle_show_options(
        query,
        user_service,
        PreferencesCategoryCodeEnum.WORK_FORMAT,
        work_format_client.get_all,
        "Выберите формат работы.\n\nℹ️ <i>Неизвестно — вакансии, у которых не удалось определить формат работы.</i>",
    )


@router.callback_query(PreferencesCallback.filter(F.action == PreferencesActionEnum.SHOW_GRADES))
async def handle_grade(query: CallbackQuery, user_service: UserService) -> None:
    await handle_show_options(
        query,
        user_service,
        PreferencesCategoryCodeEnum.GRADE,
        grade_client.get_all,
        "Выберите грейд.\n\nℹ️ <i>Неизвестно — вакансии, у которых не удалось определить формат работы.</i>",
    )


@router.callback_query(PreferencesCallback.filter(F.action == PreferencesActionEnum.SHOW_SOURCES))
async def handle_sources(query: CallbackQuery, user_service: UserService) -> None:
    await handle_show_options(
        query,
        user_service,
        PreferencesCategoryCodeEnum.SOURCE,
        vacancy_client.get_sources,
        "Источники, откуда хотите получать вакансии.\n\n"
        "ℹ️ <i>Если не выбрать ни одного — будут показаны вакансии со всех источников.</i>",
    )


@router.callback_query(PreferencesCallback.filter(F.action == PreferencesActionEnum.SELECT_OPTION))
async def handle_select_option(
    callback: CallbackQuery,
    callback_data: PreferencesCallback,
    user: UserRead,
    user_service: UserService,
    user_preferences_service: UserPreferenceService,
    uow: UnitOfWork,
) -> None:
    """Обрабатывает выбор/снятие выбора опции предпочтения."""
    category_code = callback_data.category_code
    item_id = callback_data.item_id
    if not category_code or not item_id:
        logger.error("Category code or item is empty. Callback data: %s", callback_data)
        await callback.answer("Внутренняя ошибка. Опция не найдена.", show_alert=True)
        return

    client = get_client(category_code)
    if category_code == PreferencesCategoryCodeEnum.SOURCE:
        options = await client.get_sources()  # type: ignore[attr-defined] # FIXME Сделано костыльно
    else:
        options = await client.get_all()

    item_name = ""
    for option in options:
        if option.id == item_id:
            item_name = option.name
            break

    if not item_name:
        logger.error("Option not found: %s. Options: %s. Callback data: %s", item_id, options, callback_data)
        await callback.answer("Внутренняя ошибка. Опция не найдена.", show_alert=True)
        return

    user_preference_create = UserPreferenceCreate(
        user_id=user.id,
        category_code=category_code,
        item_id=item_id,
        item_name=item_name,
    )

    await user_preferences_service.toggle_preference(user_preference_create)
    await uow.commit()

    user_with_preferences = await user_service.get_by_telegram_id(user.telegram_id, with_preferences=True)

    message = await get_message(callback)

    await safe_edit_message(
        callback,
        text=message.text or "Выберите опцию:",
        reply_markup=options_keyboard(
            category_code,
            options,
            user_with_preferences,
        ),
    )
