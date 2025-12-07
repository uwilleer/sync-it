from typing import TYPE_CHECKING

from database.models import Base
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # ex.: grade, profession, work_format
    category_code: Mapped[str] = mapped_column(String(16), index=True)

    item_id: Mapped[int] = mapped_column()
    item_name: Mapped[str] = mapped_column(String(32))

    user: Mapped["User"] = relationship(back_populates="preferences", lazy="selectin")

    __table_args__ = (UniqueConstraint("user_id", "category_code", "item_id", name="uq_user_category_item"),)
