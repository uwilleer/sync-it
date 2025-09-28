from datetime import datetime
from typing import TYPE_CHECKING

from database.models import Base
from database.models.tables import vacancy_grades_table, vacancy_skills_table, vacancy_work_formats_table
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import Grade, Profession, Skill, WorkFormat


__all__ = ["Vacancy"]


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(16), index=True)
    hash: Mapped[str] = mapped_column(String(32), unique=True)
    link: Mapped[str] = mapped_column(String(256))

    company_name: Mapped[str | None] = mapped_column(String(128))
    salary: Mapped[str | None] = mapped_column(String(96))
    workplace_description: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    conditions: Mapped[str | None] = mapped_column(Text)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    profession_id: Mapped[int | None] = mapped_column(ForeignKey("professions.id", ondelete="CASCADE"))
    profession: Mapped["Profession"] = relationship(back_populates="vacancies")

    grades: Mapped[list["Grade"]] = relationship(secondary=vacancy_grades_table, back_populates="vacancies")
    work_formats: Mapped[list["WorkFormat"]] = relationship(
        secondary=vacancy_work_formats_table, back_populates="vacancies"
    )
    skills: Mapped[list["Skill"]] = relationship(secondary=vacancy_skills_table, back_populates="vacancies")

    __table_args__ = (
        Index("idx_vacancy_published_at_id", "published_at", "id"),
        Index("idx_vacancy_source_link", "source", "link", unique=True),
    )
