from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboard.inline.buttons import (
    ChangePreferencesInlineKeyboardButton,
    MainMenuInlineKeyboardButton,
    VacanciesInlineKeyboardButton,
)


__all__ = [
    "main_keyboard",
    "main_menu_keyboard",
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для возврата в главное меню."""
    buttons = [[MainMenuInlineKeyboardButton()]]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def main_keyboard() -> InlineKeyboardMarkup:
    """Используется в главном меню или при старте бота."""
    buttons = [
        [VacanciesInlineKeyboardButton()],
        [ChangePreferencesInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()
