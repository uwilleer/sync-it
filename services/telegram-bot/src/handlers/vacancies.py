import asyncio
from collections import defaultdict
from contextlib import suppress
from typing import cast

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from callbacks.vacancy import VacancyActionEnum, VacancyCallback
from clients.schemas import SkillWithMatchSchema, SourceEnum
from clients.vacancy import vacancy_client
from commands import BotCommandEnum
from common.logger import get_logger
from database.models.enums import PreferencesCategoryCodeEnum
from exceptions import MessageNotModifiedError
from handlers.skills import update_skills
from keyboard.inline.main import main_menu_keyboard
from keyboard.inline.vacancies import vacancies_keyboard
from schemas.user import UserRead
from schemas.user_preference import UserPreferenceCreate
from unitofwork import UnitOfWork
from utils.formatters import format_publication_time
from utils.message import get_message, safe_edit_message

from services import UserPreferenceService, UserService


__all__ = ["router"]


logger = get_logger(__name__)

router = Router(name=VacancyCallback.__prefix__)


@router.message(Command(BotCommandEnum.VACANCIES))
async def handle_vacancies_command(message: Message, user_service: UserService, state: FSMContext) -> None:
    await show_vacancies(message, None, user_service, state)


@router.callback_query(VacancyCallback.filter(F.action == VacancyActionEnum.SHOW_VACANCIES))
async def handle_vacancies_callback(
    callback: CallbackQuery, callback_data: VacancyCallback, user_service: UserService, state: FSMContext
) -> None:
    await show_vacancies(callback, callback_data.vacancy_id, user_service, state)


@router.callback_query(VacancyCallback.filter(F.action == VacancyActionEnum.SELECT_SKILLS))
async def handle_vacancy_select_skills_callback(
    callback: CallbackQuery,
    callback_data: VacancyCallback,
    user: UserRead,
    user_service: UserService,
    user_preferences_service: UserPreferenceService,
    uow: UnitOfWork,
    state: FSMContext,
) -> None:
    user_preference_create = UserPreferenceCreate(
        user_id=user.id,
        category_code=PreferencesCategoryCodeEnum.SKILL,
        item_id=callback_data.skill_id,
        item_name=callback_data.skill_name,
    )

    await user_preferences_service.toggle_preference(user_preference_create)
    await uow.commit()

    await show_vacancies(callback, callback_data.vacancy_id, user_service, state)


async def show_vacancies(  # noqa: C901 PLR0912 PLR0914 PLR0915
    event: Message | CallbackQuery,
    vacancy_id: int | None,
    user_service: UserService,
    state: FSMContext,
) -> None:
    if isinstance(event, CallbackQuery):
        message = await get_message(event)
    else:
        message = event

    from_user = cast("User", event.from_user)
    user = await user_service.get_by_telegram_id(from_user.id, with_preferences=True)

    categorized_prefs = defaultdict(list)
    for pref in user.preferences:
        categorized_prefs[pref.category_code].append(pref.item_name)

    if not categorized_prefs[PreferencesCategoryCodeEnum.SKILL]:
        await message.answer(
            "Бот ориентирован под выдачу релевантных вакансий, на основе ваших навыков, "
            "но в вашем профиле они отсутствуют.\n\n"
            "Пожалуйста, добавьте навыки, чтобы мы могли подобрать для вас вакансии 😉",
        )
        await asyncio.sleep(2)
        await update_skills(message, state, need_edit=False, is_first_start=True)
        return

    sources = [str(SourceEnum.from_human(s)) for s in categorized_prefs[PreferencesCategoryCodeEnum.SOURCE]]

    result = await vacancy_client.get_by_id_with_cursor_pagination(
        current_vacancy_id=vacancy_id,
        professions=categorized_prefs[PreferencesCategoryCodeEnum.PROFESSION],
        grades=categorized_prefs[PreferencesCategoryCodeEnum.GRADE],
        work_formats=categorized_prefs[PreferencesCategoryCodeEnum.WORK_FORMAT],
        skills=categorized_prefs[PreferencesCategoryCodeEnum.SKILL],
        sources=sources,
    )
    vacancy, prev_id, next_id = result.vacancy, result.prev_id, result.next_id

    if not vacancy:
        await safe_edit_message(
            message,
            text="К сожалению, доступных вакансий нет.\n"
            "ℹ️ Скорее всего вы задали слишком строгие требования "
            "или у вас небольшое количество навыков. Проверьте ваши фильтры.\n\n",
            reply_markup=main_menu_keyboard(),
        )
        return

    user_skills = set(categorized_prefs[PreferencesCategoryCodeEnum.SKILL])
    matched_skills = list(filter(lambda s: s.name in user_skills, vacancy.skills))
    unmatched_skills = list(filter(lambda s: s.name not in user_skills, vacancy.skills))

    vacancy_text = f"<i>({vacancy.id})</i>\t"
    vacancy_text += f"<b>Должность:</b> {vacancy.profession.name if vacancy.profession else 'Неизвестно'}\n"

    if vacancy.company_name:
        vacancy_text += f"<b>Компания:</b> {vacancy.company_name}\n"
    if vacancy.grades:
        grade_names = [grade.name for grade in vacancy.grades]
        vacancy_text += f"<b>Грейд:</b> {', '.join(grade_names)}\n"
    if vacancy.salary:
        vacancy_text += f"<b>Зарплата:</b> {vacancy.salary}\n"
    if vacancy.work_formats:
        work_format_names = [work_format.name for work_format in vacancy.work_formats]
        vacancy_text += f"<b>Формат работы:</b> {', '.join(work_format_names)}\n"
    if vacancy.skills:
        matched = ", ".join(f"<code>{s.name}</code>" for s in matched_skills)
        unmatched = ", ".join(f"<s>{s.name}</s>" for s in unmatched_skills)

        vacancy_text += f"<b>Ключевые навыки:</b> {matched}, {unmatched}\n"
    if vacancy.workplace_description:
        vacancy_text += f"\n<b>О месте работы:</b>\n{vacancy.workplace_description}\n"
    if vacancy.responsibilities:
        vacancy_text += f"\n<b>Обязанности:</b>\n{vacancy.responsibilities}\n"
    if vacancy.requirements:
        vacancy_text += f"\n<b>Требования:</b>\n{vacancy.requirements}\n"
    if vacancy.conditions:
        vacancy_text += f"\n<b>Условия:</b>\n{vacancy.conditions}\n"

    vacancy_text += f"\n<b>Источник: </b>{vacancy.source.humanize()}\n"
    vacancy_text += f"\n<b>Дата публикации:</b> {format_publication_time(vacancy.published_at)}\n"

    max_text_length = 4096
    if len(vacancy_text) > max_text_length:
        vacancy_text = vacancy_text[:max_text_length]
        logger.error("Vacancy text is too long. %s, %s", vacancy.id, vacancy.link)

    matched_skill_schemas = [SkillWithMatchSchema(**s.model_dump(), is_matched=True) for s in matched_skills]
    unmatched_skill_schemas = [SkillWithMatchSchema(**s.model_dump(), is_matched=False) for s in unmatched_skills]
    skills = sorted(matched_skill_schemas + unmatched_skill_schemas, key=lambda s: s.name)

    with suppress(MessageNotModifiedError):
        await safe_edit_message(
            message,
            text=vacancy_text,
            reply_markup=vacancies_keyboard(
                skills=skills,
                vacancy_link=vacancy.link,
                previous_vacancy_id=prev_id,
                current_vacancy_id=vacancy_id or vacancy.id,
                next_vacancy_id=next_id,
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    if not vacancy_id and isinstance(event, CallbackQuery):
        await event.answer("Вакансии актуализированы")
