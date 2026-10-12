from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class KitabCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    author: str | None = Field(default=None, max_length=150)
    description: str | None = None


class KitabResponse(KitabCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KitabProgressCreate(BaseModel):
    kitab_id: int
    read_date: date
    from_reference: str | None = Field(default=None, max_length=100)
    to_reference: str | None = Field(default=None, max_length=100)
    note: str | None = Field(default=None, max_length=500)


class KitabProgressResponse(KitabProgressCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
