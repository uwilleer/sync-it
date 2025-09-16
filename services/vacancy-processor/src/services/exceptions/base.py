from typing import Any, Self

from fastapi import HTTPException
from starlette import status


class CustomHTTPException(HTTPException):
    STATUS_CODE: int
    DETAIL: str

    def __new__(cls) -> Self:
        if not hasattr(cls, "STATUS_CODE"):
            raise ValueError(f"STATUS_CODE must be set in '{cls.__name__}'")
        if not hasattr(cls, "DETAIL"):
            raise ValueError(f"STATUS_CODE must be set in '{cls.__name__}'")
        return super().__new__(cls)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class NotFoundError(CustomHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
