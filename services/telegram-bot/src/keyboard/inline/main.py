from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.main import MenuActionEnum, MenuCallback
from keyboard.buttons import MainMenuInlineKeyboardButton, VacanciesInlineKeyboardButton


__all__ = [
    "main_keyboard",
    "main_menu_keyboard",
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для возврата в главное меню."""
    buttons = [
        [MainMenuInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def main_keyboard() -> InlineKeyboardMarkup:
    """Используется в главном меню или при старте бота."""
    buttons = [
        [VacanciesInlineKeyboardButton()],
        [
            InlineKeyboardButton(
                text="⚙️ Изменить предпочтения",
                callback_data=MenuCallback(action=MenuActionEnum.SHOW_PREFERENCES).pack(),
            ),
        ],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()
