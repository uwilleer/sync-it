from fastapi import HTTPException, Request
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from starlette.responses import JSONResponse


__all__ = ["http_exception_custom_handler"]


class ErrorSchema(BaseModel):
    exc_name: str
    detail: str


async def http_exception_custom_handler(_request: Request, exc: Exception) -> JSONResponse:  # noqa: RUF029
    if not isinstance(exc, HTTPException):
        return JSONResponse({"exc_name": "internal_server_error", "detail": str(exc)}, status_code=500)

    schema = ErrorSchema(
        exc_name=to_snake(exc.__class__.__name__).lower(),
        detail=exc.detail,
    )
    data = schema.model_dump(mode="json")

    return JSONResponse(data, status_code=exc.status_code)
