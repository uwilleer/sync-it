from aiogram.types import KeyboardButton


def VacanciesKeyboardButton() -> KeyboardButton:  # noqa: N802
    return KeyboardButton(text="📋 Вакансии")


def PreferencesChangeKeyboardButton() -> KeyboardButton:  # noqa: N802
    return KeyboardButton(text="⚙️ Изменить предпочтения")
