from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.noop import NoopActionEnum, NoopCallback
from callbacks.vacancy import VacancyActionEnum, VacancyCallback
from clients.schemas import SkillWithMatchSchema
from common.shared.schemas import HttpsUrl
from keyboard.buttons import MainMenuInlineKeyboardButton


__all__ = ["vacancies_keyboard"]


def _build_skill_rows(skills: list[SkillWithMatchSchema], vacancy_id: int) -> list[list[InlineKeyboardButton]]:
    """Формирует кнопки со скиллами вакансии для переключения предпочтений."""

    rows: list[list[InlineKeyboardButton]] = []
    current_row: list[InlineKeyboardButton] = []
    max_buttons_in_row = 3  # Максимальное количество Inline кнопок в ряду
    current_row_length = 0
    max_row_length = 16  # Максимальная длина текста в одном ряду

    for skill in skills:
        skill_length = len(skill.name)

        if current_row and (
            current_row_length + skill_length > max_row_length or len(current_row) >= max_buttons_in_row
        ):
            rows.append(current_row)
            current_row = []
            current_row_length = 0

        skill_text = f"✅ {skill.name}" if skill.is_matched else f"❌ {skill.name}"

        current_row.append(
            InlineKeyboardButton(
                text=skill_text,
                callback_data=VacancyCallback(
                    vacancy_id=vacancy_id,
                    action=VacancyActionEnum.SELECT_SKILLS,
                    skill_id=skill.id,
                    skill_name=skill.name,
                ).pack(),
            )
        )
        current_row_length += skill_length

    if current_row:
        rows.append(current_row)

    return rows


def vacancies_keyboard(
    skills: list[SkillWithMatchSchema],
    vacancy_link: HttpsUrl,
    previous_vacancy_id: int | None,
    current_vacancy_id: int,
    next_vacancy_id: int | None,
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для пагинации списка вакансий и возврата в меню."""
    builder = InlineKeyboardBuilder()

    row = []
    if previous_vacancy_id:
        row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=VacancyCallback(
                    action=VacancyActionEnum.SHOW_VACANCIES,
                    vacancy_id=previous_vacancy_id,
                ).pack(),
            )
        )
    else:
        row.append(
            InlineKeyboardButton(
                text="❌",
                callback_data=NoopCallback(action=NoopActionEnum.DO_NOTHING).pack(),
            )
        )
    row.append(
        InlineKeyboardButton(
            text="Открыть",
            url=str(vacancy_link),
        )
    )
    if next_vacancy_id:
        row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=VacancyCallback(
                    action=VacancyActionEnum.SHOW_VACANCIES,
                    vacancy_id=next_vacancy_id,
                ).pack(),
            )
        )
    else:
        row.append(
            InlineKeyboardButton(
                text="❌",
                callback_data=NoopCallback(action=NoopActionEnum.DO_NOTHING).pack(),
            )
        )
    builder.row(*row)

    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить",
            callback_data=VacancyCallback(action=VacancyActionEnum.SHOW_VACANCIES).pack(),
        )
    )

    builder.row(MainMenuInlineKeyboardButton())

    matched_skill_rows = _build_skill_rows(skills, vacancy_id=current_vacancy_id)
    for row in matched_skill_rows:
        builder.row(*row)

    return builder.as_markup()
