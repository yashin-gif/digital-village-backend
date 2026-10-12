from fastapi import HTTPException

from app.core.crud import READ_LOGIN, build_crud_router
from app.core.enrich import family_head_map
from app.core.permissions import is_moderator_or_admin
from app.models.family import Family
from app.models.person import Person
from app.schemas.common import partial_model
from app.schemas.person import PersonCreate, PersonResponse
from app.utils.helpers import clean_text, normalize_blood_group


# সাধারণ সদস্যরা এই তথ্য দেখবে না — শুধু অ্যাডমিন/মডারেটর
STAFF_ONLY_FIELDS = {"date_of_birth", "is_disabled", "is_widow", "needs_assistance"}


def serialize_person(person: Person, user) -> dict:
    data = PersonResponse.model_validate(person).model_dump(mode="json")

    if user is not None and is_moderator_or_admin(user.role):
        return data

    return {key: value for key, value in data.items() if key not in STAFF_ONLY_FIELDS}


def enrich_people(db, items, user):
    """প্রতিটি সদস্যের সাথে পরিবারের প্রধানের নাম (একবারে সবার জন্য)"""
    heads = family_head_map(db, [p.family_id for p in items])

    rows = []
    for person in items:
        data = serialize_person(person, user)
        data["family_head"] = heads.get(person.family_id)
        rows.append(data)
    return rows


def prepare_person(data: dict) -> dict:
    for key in ("first_name", "last_name", "occupation", "current_location"):
        if isinstance(data.get(key), str):
            data[key] = clean_text(data[key])

    if data.get("blood_group"):
        data["blood_group"] = normalize_blood_group(data["blood_group"])

    return data


def check_family_exists(db, data: dict, current=None) -> None:
    family_id = data.get("family_id")

    if family_id is not None and not db.query(Family).filter(Family.id == family_id).first():
        raise HTTPException(status_code=404, detail="Family not found")


router = build_crud_router(
    prefix="/people",
    tags=["People"],
    model=Person,
    label="person",
    not_found="Person not found",
    create_schema=PersonCreate,
    update_schema=partial_model(PersonCreate, "PersonUpdate"),
    response_schema=PersonResponse,
    read_access=READ_LOGIN,
    prepare=prepare_person,
    validate_create=check_family_exists,
    validate_update=check_family_exists,
    enrich=enrich_people,
    default_limit=50,
    search_fields=[Person.first_name, Person.last_name, Person.phone, Person.occupation, Person.current_location],
    filters={
        "family_id": (Person.family_id, "eq"),
        "blood_group": (Person.blood_group, "eq"),
        "is_blood_donor": (Person.is_blood_donor, "eq"),
    },
)
