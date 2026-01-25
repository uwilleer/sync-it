from core import service_config
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


metadata_obj = MetaData(schema=service_config.db_schema)


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для всех моделей базы данных.

    Наследуется от DeclarativeBase и AsyncAttrs для поддержки
    асинхронных операций с базой данных. Использует схему БД,
    указанную в конфигурации сервиса.
    """

    metadata = metadata_obj
