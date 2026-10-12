from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    post_id: int
    content: str


class CommentResponse(CommentCreate):
    id: int
    author_username: str | None = None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)