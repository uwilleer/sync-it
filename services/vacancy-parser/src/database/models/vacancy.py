from datetime import datetime

from common.shared.schemas.http import HttpsUrl
from database.models import Base
from database.models.enums import SourceEnum
from sqlalchemy import DateTime, Index, String, Text, desc
from sqlalchemy.orm import Mapped, mapped_column


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID вакансии")
    source: Mapped[SourceEnum] = mapped_column(String(16), index=True, doc="Источник вакансии")
    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, doc="Хеш вакансии")
    fingerprint: Mapped[str] = mapped_column(Text, unique=True, index=True, doc="Отпечаток вакансии")
    link: Mapped[HttpsUrl] = mapped_column(String(256), unique=True, doc="Ссылка на вакансию")
    data: Mapped[str] = mapped_column(Text, doc="Сырая информация о вакансии")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, doc="Дата публикации вакансии")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), doc="Дата обработки вакансии")

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_on": source,
        "polymorphic_identity": "base",
    }

    __table_args__ = (
        Index("idx_vacancies_published_at_desc", desc("published_at")),
        Index("idx_vacancies_hash_not_processed", "hash", postgresql_where="processed_at IS NULL"),
        Index("idx_vacancies_not_processed", "processed_at", postgresql_where="processed_at IS NULL"),
        Index(
            "idx_vacancies_fingerprint_gist",
            "fingerprint",
            postgresql_using="gist",
            postgresql_ops={"fingerprint": "gist_trgm_ops"},
        ),
    )
