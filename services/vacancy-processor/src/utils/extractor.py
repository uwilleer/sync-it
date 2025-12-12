import re
from typing import Self

from common.logger import get_logger
from database.models.enums import GradeEnum, ProfessionEnum, SkillEnum, WorkFormatEnum


__all__ = ["VacancyExtractor"]


logger = get_logger(__name__)


class VacancyExtractor:
    """Класс извлечения ключевых данных из текста вакансии:
    - профессию
    - грейд
    - формат работы
    - навыки
    - описание (обязанности, требования и пр.)
    """

    # Минимальное количество навыков, для определения, что вакансия относится к IT
    NEED_SKILLS_COUNT = 5

    def __init__(self) -> None:
        self._paragraphs: list[str] | None = None

        self.company_name: str | None = None
        self.profession: ProfessionEnum = ProfessionEnum.UNKNOWN
        self.salary: str | None = None
        self.grades: set[GradeEnum] = set()
        self.work_formats: set[WorkFormatEnum] = set()
        self.skills: set[SkillEnum] = set()

        self.workplace_description: str | None = None
        self.responsibilities: str | None = None
        self.requirements: str | None = None
        self.conditions: str | None = None

    def __repr__(self) -> str:
        return f"""VacancyExtractor(
    company_name={self.company_name},
    profession={self.profession},
    salary={self.salary},
    grades={self.grades},
    work_formats={self.work_formats},
    skills={self.skills},
)"""

    @classmethod
    def extract(cls, vacancy: str) -> "Self":
        """Извлекает данные из текстового представления вакансии."""
        instance = cls()

        cleaned_vacancy = instance._clean_vacancy(vacancy)

        instance.profession = instance.extract_profession(cleaned_vacancy)

        # Нет смысла обрабатывать вакансию дальше, т.к. профессия обязательна
        if instance.profession != ProfessionEnum.UNKNOWN:
            instance.company_name = instance.extract_company_name(cleaned_vacancy)
            instance.salary = instance.extract_salary(cleaned_vacancy)
            instance.grades = instance.extract_grades(cleaned_vacancy)
            instance.work_formats = instance.extract_work_formats(cleaned_vacancy)
            instance.skills = instance.extract_skills(cleaned_vacancy)

            instance.workplace_description = instance.extract_multiline_field(cleaned_vacancy, "О месте работы")
            instance.responsibilities = instance.extract_multiline_field(cleaned_vacancy, "Обязанности")
            instance.requirements = instance.extract_multiline_field(cleaned_vacancy, "Требования")
            instance.conditions = instance.extract_multiline_field(cleaned_vacancy, "Условия")

        return instance

    def is_valid_vacancy(self, extracted_vacancy: "VacancyExtractor") -> bool:
        """Если в вакансии недостаточно навыков - скорее всего она не относиться к IT"""
        return (
            len(extracted_vacancy.skills) > self.NEED_SKILLS_COUNT
            and extracted_vacancy.profession != ProfessionEnum.UNKNOWN
        )

    @staticmethod
    def extract_company_name(text: str) -> str | None:
        """Извлекает название компании из сообщения."""
        pattern = r"Компания:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Company pattern not found in text: %s", text)
            return None

        return match.group(1).strip()

    @staticmethod
    def extract_profession(text: str) -> ProfessionEnum:
        """Извлекает профессию из сообщения."""
        pattern = r"Профессия:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Profession pattern not found in text: %s", text)
            return ProfessionEnum.UNKNOWN

        profession_str = match.group(1).strip().lower()
        if any(part in profession_str for part in ProfessionEnum.__ignore_patterns__):
            return ProfessionEnum.UNKNOWN

        profession = ProfessionEnum.get_safe(profession_str, allow_unknown=True)
        if not profession:
            logger.warning("Unknown profession part: %s", profession_str)
            return ProfessionEnum.UNKNOWN

        return profession

    @staticmethod
    def extract_salary(text: str) -> str | None:  # noqa: PLR0911
        """Извлекает зарплату из сообщения."""
        pattern = r"Зарплата:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Salary pattern not found in text: %s", text)
            return None

        salary_str = match.group(1).strip()
        if not salary_str:
            return None
        if salary_str.lower() == "неизвестно":
            return None
        if salary_str.lower() == "не указан":
            return None
        if "обсужд" in salary_str.lower():
            return None
        if "собеседов" in salary_str.lower():
            return None

        return salary_str

    @staticmethod
    def extract_grades(text: str) -> set[GradeEnum]:
        """Извлекает значение грейда из сообщения."""
        pattern = r"Позиция:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Grade pattern not found in text: %s", text)
            return {GradeEnum.UNKNOWN}

        grades: set[GradeEnum] = set()

        grade_str = match.group(1).strip()
        # Junior/Middle/Senior
        grade_parts = re.split(r"[/,()\s]+", grade_str.strip())
        joined_parts_lower = " ".join(grade_parts).lower()

        if "нет опыта" in joined_parts_lower:
            return {GradeEnum.INTERN, GradeEnum.JUNIOR}
        if "от 1 года до 3 лет" in joined_parts_lower:
            return {GradeEnum.JUNIOR, GradeEnum.MIDDLE}
        if "от 3 до 6 лет" in joined_parts_lower:
            return {GradeEnum.MIDDLE, GradeEnum.SENIOR}
        if "от 6 лет" in joined_parts_lower:
            return {GradeEnum.SENIOR, GradeEnum.LEAD}

        for part in grade_parts:
            clean_part = part.strip().lower()

            grade = GradeEnum.get_safe(clean_part, allow_unknown=True)
            if not grade:
                logger.warning("Unknown grade part: %s", clean_part)
                continue

            grades.add(grade)

        if not grades:
            grades = {GradeEnum.UNKNOWN}

        return grades

    @staticmethod
    def extract_work_formats(text: str) -> set[WorkFormatEnum]:
        """Извлекает значение формата работы из сообщения."""
        pattern = r"Формат работы:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Work format pattern not found in text: %s", text)
            return {WorkFormatEnum.UNKNOWN}

        work_formats: set[WorkFormatEnum] = set()

        work_format_str = match.group(1).strip()
        # Удаленка/Гибрид | Удаленка, Гибрид
        work_format_parts = re.split(r"[/,]+", work_format_str)

        for part in work_format_parts:
            clean_part = part.strip().lower()

            work_format = WorkFormatEnum.get_safe(clean_part, allow_unknown=True)
            if not work_format:
                logger.warning("Unknown work format part: %s", clean_part)
                continue

            work_formats.add(work_format)

        if not work_formats:
            work_formats = {WorkFormatEnum.UNKNOWN}

        return work_formats

    @staticmethod
    def extract_skills(text: str) -> set[SkillEnum]:
        """Извлекает навыки из сообщения."""
        pattern = r"Навыки:\s(.*)"
        match = re.search(pattern, text)
        if not match:
            logger.warning("Skills pattern not found in text: %s", text)
            return set()

        skills: set[SkillEnum] = set()

        skills_str = match.group(1).strip()
        # Python, Git
        skills_parts = re.split(r",", skills_str)  # noqa: RUF055 убрать noqa после добавления паттерна
        for part in skills_parts:
            clean_part = part.strip().lower()
            if any(s in clean_part for s in SkillEnum.__ignore_patterns__):
                continue

            skill = SkillEnum.get_safe(clean_part, allow_unknown=True)
            if not skill:
                logger.warning("Unknown skill part: %s", clean_part)
                continue
            if skill == SkillEnum.UNKNOWN:
                continue

            skills.add(skill)

        return skills

    def extract_multiline_field(self, message: str, field_name: str) -> str | None:
        """Извлекает многострочное текстовое поле из вакансии.

        Ищет блок с заголовком field_name, например 'Обязанности', и
        захватывает текст до следующего заголовка или конца текста.
        """
        if not self._paragraphs:
            self._paragraphs = message.split("\n\n")

        pattern = rf"{field_name}:[\s\n]*(.*?)(?=\n\n\w+:|$)"  # на эльфийском
        match = re.search(pattern, message, re.DOTALL)
        if not match:
            logger.debug('Not found multiline field: "%s" for message:\n%s', field_name, message)
            return None

        content = match.group(1).strip()
        return content or None

    @staticmethod
    def _clean_vacancy(vacancy: str) -> str:
        return (
            vacancy.replace("*", "")
            .replace("⸺", "-")  # Двойное тире
            .replace("—", "-")  # Длинное тире
            .replace("–", "-")  # Короткое тире
            .replace("―", "-")  # Горизонтальная черта
            .strip()
        )
