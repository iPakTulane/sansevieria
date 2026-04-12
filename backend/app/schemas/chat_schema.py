from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message content cannot be empty")
        return cleaned


class ChatRequest(BaseModel):
    message: str | None = Field(default=None, min_length=1, max_length=4000)
    messages: list[ChatMessage] | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def ensure_input_present(self):
        if not self.message and not self.messages:
            raise ValueError("Either 'message' or 'messages' must be provided")
        return self

    def to_message_dicts(self) -> list[dict[str, str]]:
        if self.messages:
            return [{"role": item.role, "content": item.content} for item in self.messages]
        if self.message:
            return [{"role": "user", "content": self.message}]
        return []


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str | None = None
