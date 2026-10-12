from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EducationBase(BaseModel):
    person_id: int
    education_level: str
    institution_name: str | None = None
    subject: str | None = None
    passing_year: int | None = None
    result: str | None = None
    current_status: str | None = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )