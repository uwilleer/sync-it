from enum import StrEnum

from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup
from keyboard.inline.main import main_menu_keyboard
from pydantic import BaseModel


class ResumeTypeEnum(StrEnum):
    FILE = "file"
    TEXT = "text"


class TextResumePayloadSchema(BaseModel):
    type: ResumeTypeEnum = ResumeTypeEnum.TEXT
    text: str


class FileResumePayloadSchema(BaseModel):
    type: ResumeTypeEnum = ResumeTypeEnum.FILE
    file_path: str
    suffix: str


class ResumeError(BaseModel):
    message: str
    reply_markup: InlineKeyboardMarkup = main_menu_keyboard()
    parse_mode: ParseMode = ParseMode.HTML
