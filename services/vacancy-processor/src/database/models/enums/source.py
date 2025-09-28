from enum import StrEnum


__all__ = ["SourceEnum"]


class SourceEnum(StrEnum):
    TELEGRAM = "telegram"
    HEAD_HUNTER = "head_hunter"
    HABR = "habr"
