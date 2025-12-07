from common.shared.unitofwork import BaseUnitOfWork
from repositories import UserPreferenceRepository, UserRepository


class UnitOfWork(BaseUnitOfWork):
    """Конкретная реализация UoW для SQLAlchemy."""

    users: UserRepository
    user_preferences: UserPreferenceRepository

    def init_repositories(self) -> None:
        self.users = UserRepository(self._session)
        self.user_preferences = UserPreferenceRepository(self._session)
