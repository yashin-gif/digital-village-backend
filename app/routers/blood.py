from fastapi import HTTPException

from app.core.crud import READ_LOGIN, build_crud_router
from app.core.enrich import person_map
from app.dependencies import get_current_user
from app.models.blood import BloodDonor
from app.models.person import Person
from app.schemas.blood import BloodDonorCreate, BloodDonorResponse
from app.schemas.common import partial_model
from app.utils.helpers import normalize_blood_group


def check_donor_person(db, data: dict, current: BloodDonor | None = None) -> None:
    person_id = data.get("person_id")

    if person_id is None:
        return

    if not db.query(Person).filter(Person.id == person_id).first():
        raise HTTPException(status_code=404, detail="Person not found")

    query = db.query(BloodDonor).filter(BloodDonor.person_id == person_id)
    if current is not None:
        query = query.filter(BloodDonor.id != current.id)

    if query.first():
        raise HTTPException(
            status_code=400,
            detail="This person is already registered as a blood donor",
        )


def prepare_donor(data: dict) -> dict:
    if data.get("blood_group"):
        data["blood_group"] = normalize_blood_group(data["blood_group"])

    return data


def enrich_blood(db, items, user):
    """দাতার নাম, ফোন ও এলাকা। ফোন শুধু লগইন করা সদস্যের জন্য (এই এন্ডপয়েন্ট লগইন চায়)।"""
    people = person_map(db, [d.person_id for d in items])

    rows = []
    for donor in items:
        data = BloodDonorResponse.model_validate(donor).model_dump(mode="json")
        person = people.get(donor.person_id)
        data["person_name"] = (
            " ".join(p for p in [person.first_name, person.last_name] if p) if person else None
        )
        data["person_phone"] = person.phone if person else None
        data["person_location"] = person.current_location if person else None
        rows.append(data)
    return rows


# যোগ করা: যে কোনো লগইন সদস্য। দেখা: শুধু লগইন করা সদস্য (ফোন নম্বর আছে বলে)।
router = build_crud_router(
    prefix="/blood",
    tags=["Blood"],
    model=BloodDonor,
    label="blood_donor",
    not_found="Blood donor not found",
    create_schema=BloodDonorCreate,
    update_schema=partial_model(BloodDonorCreate, "BloodDonorUpdate"),
    response_schema=BloodDonorResponse,
    read_access=READ_LOGIN,
    create_guard=get_current_user,
    prepare=prepare_donor,
    validate_create=check_donor_person,
    validate_update=check_donor_person,
    enrich=enrich_blood,
    default_limit=50,
    filters={
        "blood_group": (BloodDonor.blood_group, "eq"),
        "is_available": (BloodDonor.is_available, "eq"),
    },
    sort_column=BloodDonor.id,
)
