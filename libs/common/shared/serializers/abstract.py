from abc import ABC, abstractmethod
from typing import Any


class AbstractSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """Сериализует объект в бинарный формат"""

    @abstractmethod
    def deserialize(self, obj: bytes) -> Any:
        """Восстанавливает объект из бинарных данных"""
