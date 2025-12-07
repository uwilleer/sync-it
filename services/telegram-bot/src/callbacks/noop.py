from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class NoopActionEnum(StrEnum):
    DO_NOTHING = "do_nothing"


class NoopCallback(CallbackData, prefix="noop"):
    action: NoopActionEnum = NoopActionEnum.DO_NOTHING
