from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmergencyCreate(BaseModel):
    emergency_type: str
    title: str
    description: str
    contact_phone: str | None = None
    location: str | None = None


class EmergencyResponse(EmergencyCreate):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)