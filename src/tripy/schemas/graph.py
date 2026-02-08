from __future__ import annotations

from pydantic import BaseModel, Field


class GraphRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = Field(default=None, max_length=128)


class GraphResponse(BaseModel):
    assistant: str
    thread_id: str
    interrupted: bool = False
