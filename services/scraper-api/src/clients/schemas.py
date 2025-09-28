from pydantic import BaseModel


__all__ = [
    "PingResponse",
    "TelegramDetailedMessageParams",
]


class PingResponse(BaseModel):
    status: str = "pong"


class TelegramDetailedMessageParams(BaseModel):
    before: int
