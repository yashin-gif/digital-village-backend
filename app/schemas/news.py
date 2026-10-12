from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsCreate(BaseModel):
    title: str
    content: str
    is_published: bool = True


class NewsResponse(NewsCreate):
    id: int
    created_at: datetime
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)