from typing import Any, get_args, get_origin

from common.shared.schemas.model.utils import col
from pydantic import Field
from pydantic.fields import FieldInfo
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import ColumnProperty, RelationshipProperty


def _is_optional_type(annotation: Any) -> bool:
    """Проверяет, является ли тип аннотации Optional (Union[T, None] или T | None)."""
    if annotation is None or annotation is type(None):
        return True

    origin = get_origin(annotation)
    if origin is None:
        return False

    # Проверяем Union[T, None] или T | None
    if origin is type(None) or origin is type(Any):
        return True

    args = get_args(annotation)
    if not args:
        return False

    # Проверяем Union[...] или | синтаксис
    return type(None) in args or Any in args


class ModelFieldsMeta(type):
    def __new__(  # noqa: PLR0914 C901
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

        # Объединяем аннотации из namespace и базовых классов
        declared_annotations = dict(namespace.get("__annotations__", {}))
        # Добавляем аннотации из базовых классов, если они есть
        for base in bases:
            base_annotations = getattr(base, "__annotations__", {})
            declared_annotations.update(base_annotations)

        declared_attrs = set(namespace.keys())
        mapper = inspect(model)
        columns = {attr.key: attr for attr in mapper.attrs if isinstance(attr, ColumnProperty)}
        relationships = {attr.key: attr for attr in mapper.attrs if isinstance(attr, RelationshipProperty)}

        for field_name in (*columns, *relationships):
            if field_name not in declared_annotations and field_name not in declared_attrs:
                raise AttributeError(f"{cls.__name__}.{field_name} is not defined")

            # Проверка соответствия типов для колонок
            if field_name in columns:
                model_attr = getattr(model, field_name)
                column = model_attr.property.columns[0]
                is_nullable = column.nullable

                # Получаем аннотацию типа из ModelFields
                field_annotation = declared_annotations.get(field_name)
                if field_annotation is not None:
                    annotation_allows_none = _is_optional_type(field_annotation)

                    # Проверяем соответствие nullable статуса колонки и типа аннотации
                    if is_nullable and not annotation_allows_none:
                        raise TypeError(
                            f"{cls.__name__}.{field_name}: SQLAlchemy column is nullable, "
                            f"but type annotation '{field_annotation.__name__}' does not allow None. "
                            f"Use '{field_annotation.__name__} | None' or 'Optional[{field_annotation.__name__}]'"
                        )
                    if not is_nullable and annotation_allows_none:
                        raise TypeError(
                            f"{cls.__name__}.{field_name}: SQLAlchemy column is not nullable, "
                            f"but type annotation '{field_annotation}' allows None. "
                            f"Remove 'None' or 'Optional' from the type annotation"
                        )

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
