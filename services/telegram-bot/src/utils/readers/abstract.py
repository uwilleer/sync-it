from abc import ABC, abstractmethod


__all__ = ["AbstractFileReader"]


class AbstractFileReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> str:
        pass
