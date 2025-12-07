from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboard.inline.buttons import (
    BackToPreferencesInlineKeyboardButton,
    BackToSkillsInlineKeyboardButton,
    ImportSkillsInlineKeyboardButton,
    MainMenuInlineKeyboardButton,
    VacanciesInlineKeyboardButton,
)


def update_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для обновленных навыков."""
    buttons = [
        [BackToSkillsInlineKeyboardButton()],
        [MainMenuInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def process_update_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для процесса обновленных навыков."""
    buttons = [
        [VacanciesInlineKeyboardButton()],
        [BackToSkillsInlineKeyboardButton()],
        [MainMenuInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def show_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для просмотра/изменения навыков."""
    buttons = [
        [ImportSkillsInlineKeyboardButton()],
        [VacanciesInlineKeyboardButton()],
        [BackToPreferencesInlineKeyboardButton()],
        [MainMenuInlineKeyboardButton()],
    ]
    return InlineKeyboardBuilder(markup=buttons).as_markup()
