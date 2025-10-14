from datetime import datetime

from database.models import Base
from sqlalchemy import DateTime, Index, String, Text, desc
from sqlalchemy.orm import Mapped, mapped_column


__all__ = ["Vacancy"]


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(16), index=True)

    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    fingerprint: Mapped[str] = mapped_column(Text, unique=True, index=True)
    link: Mapped[str] = mapped_column(String(256), unique=True)
    data: Mapped[str] = mapped_column(Text)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_on": source,
        "polymorphic_identity": "base",
    }

    __table_args__ = (
        Index("idx_vacancies_published_at_desc", desc("published_at")),
        Index("idx_vacancies_hash_not_processed", "hash", postgresql_where="processed_at IS NULL"),
        Index("idx_vacancies_not_processed", "processed_at", postgresql_where="processed_at IS NULL"),
        Index(
            "idx_vacancies_fingerprint_trgm",
            "fingerprint",
            postgresql_using="gist",
            postgresql_ops={"fingerprint": "gist_trgm_ops"},
        ),
    )
