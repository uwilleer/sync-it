from database.models import Vacancy
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


__all__ = ["TelegramVacancy"]


class TelegramVacancy(Vacancy):
    __tablename__ = "telegram_vacancies"

    id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"), primary_key=True)

    channel_username: Mapped[str] = mapped_column(String(32))
    message_id: Mapped[int] = mapped_column()

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": "telegram",
    }
