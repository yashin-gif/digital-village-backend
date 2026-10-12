from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstitutionCreate(BaseModel):
    name: str
    institution_type: str
    address: str | None = None
    phone: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class InstitutionResponse(BaseModel):
    id: int
    name: str
    institution_type: str
    address: str | None
    phone: str | None
    description: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)