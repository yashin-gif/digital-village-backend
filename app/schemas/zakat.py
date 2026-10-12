from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ZakatCreate(BaseModel):
    person_id: int | None = None
    record_type: str
    amount: int | None = None
    description: str | None = None


class ZakatResponse(ZakatCreate):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)