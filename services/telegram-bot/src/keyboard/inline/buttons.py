from aiogram.types import InlineKeyboardButton
from callbacks.main import MenuActionEnum, MenuCallback
from callbacks.noop import NoopActionEnum, NoopCallback
from callbacks.preferences import PreferencesActionEnum, PreferencesCallback
from callbacks.skill import SkillActionEnum, SkillCallback
from callbacks.vacancy import VacancyActionEnum, VacancyCallback


# TODO: Дублируется текст в inline/buttons и reply/buttons. Можно сделать один Enum


def EmptyDashedKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="—————————",
        callback_data=NoopCallback(action=NoopActionEnum.DO_NOTHING).pack(),
    )


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


def ChangePreferencesInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="⚙️ Изменить предпочтения",
        callback_data=MenuCallback(action=MenuActionEnum.SHOW_PREFERENCES).pack(),
    )


def ImportSkillsInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="📥 Импортировать навыки",
        callback_data=SkillCallback(action=SkillActionEnum.UPDATE_SKILLS).pack(),
    )


def BackToSkillsInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🔙 К навыкам",
        callback_data=SkillCallback(action=SkillActionEnum.TOGGLE_SKILLS).pack(),
    )


def BackToPreferencesInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🔙 К предпочтениям",
        callback_data=MenuCallback(action=MenuActionEnum.SHOW_PREFERENCES).pack(),
    )


def ProfessionInlineKeyboardButton() -> InlineKeyboardButton:  # noqa: N802
    return InlineKeyboardButton(
        text="🎯 Профессия",
        callback_data=PreferencesCallback(action=PreferencesActionEnum.SHOW_PROFESSIONS).pack(),
    )
