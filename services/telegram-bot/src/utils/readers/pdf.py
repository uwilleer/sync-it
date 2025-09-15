from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfReader as PyPdfReader
from pytesseract import image_to_string  # type: ignore[import-untyped]
from utils.readers import AbstractFileReader


__all__ = ["PdfReader"]


class PdfReader(AbstractFileReader):
    MIN_TEXT_LEN = 300  # если текста меньше этого количества символов, считаем сканом

    def read(self, file_path: str) -> str:
        path = Path(file_path)
        texts = []

        with path.open("rb") as file:
            reader = PyPdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    texts.append(text)

        joined_text = "\n".join(texts)

        if len(joined_text) < self.MIN_TEXT_LEN:
            texts = []
            images = convert_from_path(file_path)
            for img in images:
                text = image_to_string(img, lang="eng+rus")
                if text.strip():
                    texts.append(text)
            joined_text = "\n".join(texts)

        return joined_text
