from datetime import UTC, datetime
from typing import TYPE_CHECKING

from database.models import Base
from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import UserPreference


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class User(Base):
    """Модель пользователя Telegram бота.

    Хранит информацию о пользователе, включая его Telegram ID, имя, фамилию,
    имя пользователя и временные метки создания и последней активности.
    Связана с предпочтениями пользователя через отношение one-to-many.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID пользователя")
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, doc="Уникальный ID пользователя в Telegram")

    username: Mapped[str | None] = mapped_column(String(32), doc="Имя пользователя в Telegram")
    first_name: Mapped[str] = mapped_column(String(64), doc="Имя пользователя")
    last_name: Mapped[str | None] = mapped_column(String(64), doc="Фамилия пользователя")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, doc="Дата и время регистрации пользователя"
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        doc="Дата и время последней активности пользователя",
    )

    preferences: Mapped[list["UserPreference"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Список предпочтений пользователя (профессии, навыки, грейды и т.д.)",
    )
