from pydantic import BaseModel


__all__ = [
    "ProfessionResponse",
    "ProfessionSchema",
]


class ProfessionSchema(BaseModel):
    id: int
    name: str


class ProfessionResponse(BaseModel):
    professions: list[ProfessionSchema]
