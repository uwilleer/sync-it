from typing import Any, Protocol


class SupportsGetAll(Protocol):
    async def get_all(self) -> list[Any]: ...
