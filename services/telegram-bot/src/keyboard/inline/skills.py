from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.skill import SkillActionEnum, SkillCallback
from keyboard.inline.buttons import (
    BackToPreferencesInlineKeyboardButton,
    MainMenuInlineKeyboardButton,
    VacanciesInlineKeyboardButton,
)


__all__ = [
    "process_update_skills_keyboard",
    "show_skills_keyboard",
    "update_skills_keyboard",
]


def update_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для обновленных навыков."""
    buttons = [
        [
            InlineKeyboardButton(
                text="🔙 К навыкам",
                callback_data=SkillCallback(action=SkillActionEnum.TOGGLE_SKILLS).pack(),
            ),
        ],
        [MainMenuInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def process_update_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для процесса обновленных навыков."""
    buttons = [
        [VacanciesInlineKeyboardButton()],
        [MainMenuInlineKeyboardButton()],
    ]

    return InlineKeyboardBuilder(markup=buttons).as_markup()


def show_skills_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для просмотра/изменения навыков."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📥 Импортировать навыки",
                callback_data=SkillCallback(action=SkillActionEnum.UPDATE_SKILLS).pack(),
            ),
        ],
        [VacanciesInlineKeyboardButton()],
        [BackToPreferencesInlineKeyboardButton()],
        [MainMenuInlineKeyboardButton()],
    ]
    return InlineKeyboardBuilder(markup=buttons).as_markup()
