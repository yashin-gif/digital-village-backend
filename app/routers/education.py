from fastapi import HTTPException

from app.core.crud import READ_LOGIN, build_crud_router
from app.core.enrich import person_name_map
from app.models.education import Education
from app.models.person import Person
from app.schemas.common import partial_model
from app.schemas.education import EducationCreate, EducationResponse


def check_person(db, data: dict, current=None) -> None:
    person_id = data.get("person_id")

    if person_id is not None and not db.query(Person).filter(Person.id == person_id).first():
        raise HTTPException(status_code=404, detail="Person not found")


def enrich_education(db, items, user):
    names = person_name_map(db, [e.person_id for e in items])

    rows = []
    for item in items:
        data = EducationResponse.model_validate(item).model_dump(mode="json")
        data["person_name"] = names.get(item.person_id)
        rows.append(data)
    return rows


router = build_crud_router(
    prefix="/education",
    tags=["Education"],
    model=Education,
    label="education",
    not_found="Education record not found",
    create_schema=EducationCreate,
    update_schema=partial_model(EducationCreate, "EducationUpdate"),
    response_schema=EducationResponse,
    read_access=READ_LOGIN,
    validate_create=check_person,
    validate_update=check_person,
    enrich=enrich_education,
    default_limit=50,
    search_fields=[Education.education_level, Education.institution_name, Education.subject],
    filters={"person_id": (Education.person_id, "eq")},
)
