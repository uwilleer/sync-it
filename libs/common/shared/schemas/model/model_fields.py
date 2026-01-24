from typing import Any

from common.shared.schemas.model.utils import col
from pydantic import Field
from pydantic.fields import FieldInfo
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import ColumnProperty, RelationshipProperty


class ModelFieldsMeta(type):
    def __new__(
        mcls: Any,
        name: Any,
        bases: Any,
        namespace: dict[str, Any],
        **_: dict[str, Any],
    ) -> type:
        cls = super().__new__(mcls, name, bases, dict(namespace))

        if name == "ModelFields":
            return cls  # type: ignore[no-any-return]

        model = namespace.get("__model__")
        if model is None:
            raise AssertionError(f"{name}.__model__ is not defined")

        declared_annotations = namespace.get("__annotations__", {})  # FIXME Проверить всегда ли default
        declared_attrs = set(namespace.keys())
        mapper = inspect(model)
        columns = {attr.key: attr for attr in mapper.attrs if isinstance(attr, ColumnProperty)}
        relationships = {attr.key: attr for attr in mapper.attrs if isinstance(attr, RelationshipProperty)}

        for field_name in (*columns, *relationships):
            if field_name not in declared_annotations and field_name not in declared_attrs:
                raise AttributeError(f"{cls.__name__}.{field_name} is not defined")

            model_attr = getattr(model, field_name)
            default_data = col(model_attr)
            custom_attr: FieldInfo | None = getattr(cls, field_name, None)

            if custom_attr is None:
                setattr(cls, field_name, Field(**default_data))
                continue

            reversed_metadata_lookup = {v: k for k, v in FieldInfo.metadata_lookup.items()}
            for md in custom_attr.metadata:
                key = reversed_metadata_lookup[md.__class__]
                value = getattr(md, key)
                default_data[key] = value

            setattr(cls, field_name, Field(**default_data))

        return cls  # type: ignore[no-any-return]


class ModelFields(metaclass=ModelFieldsMeta):
    __model__: type
