from pathlib import Path
from typing import ClassVar

from utils.readers import AbstractFileReader, PdfReader, TxtReader
from utils.readers.enums import SupportedReaderExtensionsEnum
from utils.text_extractor.exceptions import UnsupportedFileTypeError


__all__ = ["TextExtractor"]


class TextExtractor:
    readers_map: ClassVar[dict[SupportedReaderExtensionsEnum, AbstractFileReader]] = {
        SupportedReaderExtensionsEnum.TXT: TxtReader(),
        SupportedReaderExtensionsEnum.PDF: PdfReader(),
    }

    def read(self, file_name: str) -> str:
        ext_str = Path(file_name).suffix.lower()
        try:
            ext_enum = SupportedReaderExtensionsEnum(ext_str)
        except ValueError as e:
            raise UnsupportedFileTypeError(f"Unsupported file type: {ext_str}") from e

        reader = self.readers_map[ext_enum]
        return reader.read(file_name)
