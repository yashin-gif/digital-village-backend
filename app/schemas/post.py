from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(PostCreate):
    id: int
    author_username: str | None = None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)