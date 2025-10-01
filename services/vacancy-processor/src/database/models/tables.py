from database.models import Base
from sqlalchemy import Column, ForeignKey, Table, Index


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

# Reverse index to speed up lookups by grade -> vacancies
Index(
    "idx_vacancy_grades_grade_id_vacancy_id",
    vacancy_grades_table.c.grade_id,
    vacancy_grades_table.c.vacancy_id,
)

vacancy_skills_table: Table = Table(
    "vacancy_skills",
    Base.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="RESTRICT"), primary_key=True),
)

# Reverse index to speed up lookups by skill -> vacancies (used in relevance calc)
Index(
    "idx_vacancy_skills_skill_id_vacancy_id",
    vacancy_skills_table.c.skill_id,
    vacancy_skills_table.c.vacancy_id,
)


vacancy_work_formats_table: Table = Table(
    "vacancy_work_formats",
    Base.metadata,
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
    Column("work_format_id", ForeignKey("work_formats.id", ondelete="RESTRICT"), primary_key=True),
)

# Reverse index to speed up lookups by work_format -> vacancies
Index(
    "idx_vacancy_work_formats_work_format_id_vacancy_id",
    vacancy_work_formats_table.c.work_format_id,
    vacancy_work_formats_table.c.vacancy_id,
)
