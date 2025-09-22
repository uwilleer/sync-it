from pydantic import BaseModel
from tasks.enums import ResumeTypeEnum


__all__ = ["FileResumePayloadSchema", "TextResumePayloadSchema"]


class TextResumePayloadSchema(BaseModel):
    type: ResumeTypeEnum = ResumeTypeEnum.TEXT
    text: str


class FileResumePayloadSchema(BaseModel):
    type: ResumeTypeEnum = ResumeTypeEnum.FILE
    file_path: str
    suffix: str
