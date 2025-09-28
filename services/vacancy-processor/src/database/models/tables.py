from database.models import Base
from sqlalchemy import Column, ForeignKey, Table


__all__ = [
    "vacancy_grades_table",
    "vacancy_skills_table",
    "vacancy_work_formats_table",
]


vacancy_grades_table: Table = Table(
    "vacancy_grades",
    Base.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
    Column("grade_id", ForeignKey("grades.id", ondelete="RESTRICT"), primary_key=True),
)

vacancy_skills_table: Table = Table(
    "vacancy_skills",
    Base.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="RESTRICT"), primary_key=True),
)


vacancy_work_formats_table: Table = Table(
    "vacancy_work_formats",
    Base.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
    Column("work_format_id", ForeignKey("work_formats.id", ondelete="RESTRICT"), primary_key=True),
)
