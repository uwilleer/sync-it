from typing import TYPE_CHECKING

from database.models import Base
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    from database.models import User


class UserPreference(Base):
    """Модель предпочтений пользователя.

    Хранит выбранные пользователем элементы различных категорий:
    профессии, навыки, грейды, форматы работы, источники вакансий.
    Один пользователь может иметь множество предпочтений разных категорий.
    """

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, doc="ID предпочтения")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), doc="ID пользователя, которому принадлежит предпочтение"
    )

    # ex.: grade, profession, work_format
    category_code: Mapped[str] = mapped_column(String(16), index=True, doc="Код категории предпочтения")

    item_id: Mapped[int] = mapped_column(doc="ID элемента в соответствующей категории")
    item_name: Mapped[str] = mapped_column(String(32), doc="Название элемента для отображения")

    user: Mapped["User"] = relationship(
        back_populates="preferences", lazy="selectin", doc="Пользователь, которому принадлежит предпочтение"
    )

    __table_args__ = (UniqueConstraint("user_id", "category_code", "item_id", name="uq_user_category_item"),)
