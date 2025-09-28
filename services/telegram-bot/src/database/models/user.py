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
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    username: Mapped[str | None] = mapped_column(String(32))
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    preferences: Mapped[list["UserPreference"]] = relationship(
        back_populates="users",
        cascade="all, delete-orphan",
    )
