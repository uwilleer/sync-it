import hashlib
import re

from common.logger import get_logger
from constants.fingerprint import FINGERPRINT_STOPWORDS
from database.models.enums import SourceEnum


__all__ = [
    "clear_html",
    "generate_fingerprint",
    "generate_hash",
    "generate_vacancy_hash",
]


logger = get_logger(__name__)


def generate_hash(value: str | int, algorithm: str = "md5") -> str:
    """Генерирует хеш на основе переданного значения и алгоритма."""
    hasher = hashlib.new(algorithm)

    value = str(value)
    hasher.update(value.encode("utf-8"))

    return hasher.hexdigest()


def generate_vacancy_hash(value: str | int, source: SourceEnum) -> str:
    """Генерирует хеш на основе переданного значения и источника,
    чтобы избежать возможный конфликт дублирования значений."""
    return generate_hash(f"{source.value}_{value}")


def truncate_by_bytes(s: str, max_bytes: int) -> str:
    """
    Обрезает строку, чтобы ее UTF-8 представление не превышало max_bytes.

    :param s: Исходная строка.
    :param max_bytes: Максимальное количество байт.
    """
    encoded_s = s.encode("utf-8")

    if len(encoded_s) <= max_bytes:
        return s

    truncated_bytes = encoded_s[:max_bytes]

    return truncated_bytes.decode("utf-8", errors="ignore")


def generate_fingerprint(text: str) -> str:
    """
    Генерирует fingerprint (отпечаток) на основе переданного текста.
    Fingerprint используется для поиска одинаковых вакансий на уровне БД, используя расширение pg_trgm.

    Пример:
    >>> generate_fingerprint("3+ years. Junior/Middle Python developer; (Ex@mp1e c0mpany) #deleted")
    '(exmp1e 3 c0mpany) developer; junior/middle python years.'
    """
    # Удаляем слова, начинающиеся с хештега
    text = re.sub(r"#\w+\s*", "", text)
    # Удаляем URL-адресы
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Удаляем лишние символы
    text = re.sub(r"[^а-яa-z0-9/;().\s]", "", text.lower())
    filtered_words = [word for word in text.split() if word not in FINGERPRINT_STOPWORDS]
    sorted_words = sorted(filtered_words)
    split_words = " ".join(sorted_words)

    # 2704 - максимальная длина байтов для индекса в БД
    return truncate_by_bytes(split_words, 2704)


def clear_html(text: str) -> str:
    """Убирает HTML-теги из текста."""
    return re.sub(r"(<[^>]*>)|(&quot;)", "", text)
