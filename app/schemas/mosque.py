from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MosqueCreate(BaseModel):
    name: str
    address: str | None = None
    imam_name: str | None = None
    contact_phone: str | None = None
    description: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class MosqueResponse(MosqueCreate):
    id: int
    created_at: datetime
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)