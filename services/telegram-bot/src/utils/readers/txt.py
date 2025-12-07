from pathlib import Path

from utils.readers import AbstractFileReader


class TxtReader(AbstractFileReader):
    def read(self, file_path: str) -> str:  # noqa: PLR6301
        return Path(file_path).read_text(encoding="utf-8")
