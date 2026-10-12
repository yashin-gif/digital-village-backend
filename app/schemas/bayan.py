from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BayanCreate(BaseModel):
    mosque_id: int | None = None
    title: str = Field(min_length=2, max_length=200)
    speaker_name: str | None = Field(default=None, max_length=150)
    session_date: date
    media_url: str | None = Field(default=None, max_length=500)
    description: str | None = None
    is_published: bool = True


class BayanResponse(BayanCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
