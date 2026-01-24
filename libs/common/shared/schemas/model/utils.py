from typing import Any

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.orm import InstrumentedAttribute


def col(model_field: InstrumentedAttribute[Any]) -> dict[str, Any]:
    # FIXME: Doc
    data: dict[str, Any] = {}

    try:
        column = model_field.property.columns[0]
    except NoForeignKeysError:
        # relationship или свойство без колонок
        data["description"] = getattr(model_field.info, "doc", None)
        return data
    except AttributeError:
        data["description"] = getattr(model_field, "__doc__", None)
        return data

    # Документация
    data["description"] = getattr(column, "doc", None)

    # Типовая валидация
    col_type = column.type
    if isinstance(col_type, (Integer, BigInteger)):
        if column.primary_key:
            data["ge"] = 1
    elif isinstance(col_type, String):
        data["max_length"] = getattr(col_type, "length", None)
    elif isinstance(col_type, DateTime):
        pass
    else:
        raise TypeError(f"Unsupported column type: {col_type}")

    # Значение по умолчанию, если оно задано
    if column.default is not None and column.default.is_scalar:
        data["default"] = column.default.arg

    return data
