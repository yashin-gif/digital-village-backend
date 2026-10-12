from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlaceCreate(BaseModel):
    name: str
    place_type: str
    description: str | None = None
    address: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class PlaceResponse(PlaceCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)