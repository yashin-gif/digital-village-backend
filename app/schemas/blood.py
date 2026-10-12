from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BloodDonorCreate(BaseModel):
    person_id: int
    blood_group: str
    is_available: bool = True
    last_donation_date: datetime | None = None
    notes: str | None = None


class BloodDonorResponse(BaseModel):
    id: int
    person_id: int
    blood_group: str
    is_available: bool
    last_donation_date: datetime | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)