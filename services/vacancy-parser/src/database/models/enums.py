from enum import StrEnum
from typing import Self


class BaseStrEnum(StrEnum):
    @classmethod
    def get_safe(cls, label: str) -> Self | None:
        """Возвращает элемент Enum по строковому значению, с игнорированием регистра."""
        for member in cls:
            if member.value.lower() == label.lower():
                return member
        return None


class SourceEnum(BaseStrEnum):
    TELEGRAM = "telegram"
    HEAD_HUNTER = "head_hunter"
    HABR = "habr"
