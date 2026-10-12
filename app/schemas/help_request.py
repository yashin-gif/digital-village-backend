from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HelpRequestCreate(BaseModel):
    person_id: int | None = None
    request_type: str
    title: str
    description: str


class HelpRequestResponse(HelpRequestCreate):
    id: int
    user_id: int | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)