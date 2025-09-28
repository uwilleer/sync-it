from enum import StrEnum


__all__ = ["ServiceEnum"]


class ServiceEnum(StrEnum):
    SCRAPER_API = "scraper-api"
    TELEGRAM_BOT = "telegram-bot"
    GPT_API = "gpt-api"
    VACANCY_PARSER = "vacancy-parser"
    VACANCY_PROCESSOR = "vacancy-processor"
