from abc import ABC, abstractmethod


class AbstractFileReader(ABC):
    @abstractmethod
    def read(self, file_path: str) -> str:
        pass
