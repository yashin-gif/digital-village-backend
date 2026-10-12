from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    is_active: bool = True


class AnnouncementResponse(AnnouncementCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)