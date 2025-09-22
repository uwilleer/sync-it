from aiogram.types import InlineKeyboardButton
from callbacks.main import MenuActionEnum, MenuCallback
from callbacks.preferences import PreferencesActionEnum, PreferencesCallback
from callbacks.vacancy import VacancyActionEnum, VacancyCallback


__all__ = [
    "BackToPreferencesInlineKeyboardButton",
    "MainMenuInlineKeyboardButton",
    "ProfessionInlineKeyboardButton",
    "VacanciesInlineKeyboardButton",
]


def MainMenuInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🏠 В меню",
        callback_data=MenuCallback(action=MenuActionEnum.SHOW_MAIN).pack(),
    )


def VacanciesInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="📋 Вакансии",
        callback_data=VacancyCallback(action=VacancyActionEnum.SHOW_VACANCIES).pack(),
    )


def BackToPreferencesInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🔙 К предпочтениям",
        callback_data=MenuCallback(action=MenuActionEnum.SHOW_PREFERENCES).pack(),
    )


def ProfessionInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🎯 Направление",
        callback_data=PreferencesCallback(action=PreferencesActionEnum.SHOW_PROFESSIONS).pack(),
    )
