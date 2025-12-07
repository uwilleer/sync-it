from aiogram.types import ReplyKeyboardMarkup
from keyboard.reply.buttons import PreferencesChangeKeyboardButton, VacanciesKeyboardButton


def general_keyboard() -> ReplyKeyboardMarkup:
    """Создает кнопки для навигации во всем приложении."""
    buttons = [
        [VacanciesKeyboardButton(), PreferencesChangeKeyboardButton()],
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
