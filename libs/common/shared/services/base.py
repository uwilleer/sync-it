from common.shared.unitofwork import BaseUnitOfWork


class BaseUOWService[UnitOfWorkType: BaseUnitOfWork]:
    def __init__(self, uow: UnitOfWorkType) -> None:
        self._uow = uow

    async def commit(self) -> None:
        await self._uow.commit()
