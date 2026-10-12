from fastapi import HTTPException

from app.core.crud import READ_STAFF, build_crud_router
from app.core.enrich import person_name_map
from app.models.person import Person
from app.models.zakat import ZakatRecord
from app.schemas.common import partial_model
from app.schemas.zakat import ZakatCreate, ZakatResponse


def check_zakat(db, data: dict, current=None) -> None:
    person_id = data.get("person_id")

    if person_id is not None and not db.query(Person).filter(Person.id == person_id).first():
        raise HTTPException(status_code=404, detail="Person not found")

    amount = data.get("amount")

    if amount is not None and amount < 0:
        raise HTTPException(status_code=400, detail="Amount cannot be negative")


def enrich_zakat(db, items, user):
    names = person_name_map(db, [z.person_id for z in items])

    rows = []
    for item in items:
        data = ZakatResponse.model_validate(item).model_dump(mode="json")
        data["person_name"] = names.get(item.person_id)
        rows.append(data)
    return rows


# যাকাতের হিসাব সম্পূর্ণ আর্থিক ও ব্যক্তিগত তথ্য — শুধু মডারেটর/অ্যাডমিন
router = build_crud_router(
    prefix="/zakat",
    tags=["Zakat"],
    model=ZakatRecord,
    label="zakat",
    not_found="Zakat record not found",
    create_schema=ZakatCreate,
    update_schema=partial_model(ZakatCreate, "ZakatUpdate"),
    response_schema=ZakatResponse,
    read_access=READ_STAFF,
    validate_create=check_zakat,
    validate_update=check_zakat,
    enrich=enrich_zakat,
    default_limit=50,
    search_fields=[ZakatRecord.record_type, ZakatRecord.description, ZakatRecord.status],
    filters={
        "person_id": (ZakatRecord.person_id, "eq"),
        "record_type": (ZakatRecord.record_type, "eq"),
        "status": (ZakatRecord.status, "eq"),
    },
)
