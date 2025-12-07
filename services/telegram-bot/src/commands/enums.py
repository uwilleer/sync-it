from enum import StrEnum
from typing import Self


class CommandEnum(StrEnum):
    """
    Класс для перечисления команд бота.

    Добавляет к StrEnum поле description для хранения описания команд.
    """

    _description_: str

    @property
    def description(self) -> str:
        return self._description_

    def __new__(cls, value: str, description: str) -> Self:
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj._description_ = description
        return obj
