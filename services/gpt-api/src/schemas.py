from pydantic import BaseModel, ConfigDict


class PromptRequest(BaseModel):
    prompt: str

    model_config = ConfigDict(extra="forbid")


class PromptResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
