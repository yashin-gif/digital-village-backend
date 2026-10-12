from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PersonBase(BaseModel):
    family_id: int
    first_name: str
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    blood_group: str | None = None
    occupation: str | None = None
    current_location: str | None = None

    is_disabled: bool = False
    is_widow: bool = False
    needs_assistance: bool = False
    is_blood_donor: bool = False


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)