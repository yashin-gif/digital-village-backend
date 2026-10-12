from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FamilyBase(BaseModel):
    family_code: str
    head_name: str
    village: str
    address: str | None = None
    phone: str | None = None


class FamilyCreate(FamilyBase):
    pass


class FamilyResponse(FamilyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)