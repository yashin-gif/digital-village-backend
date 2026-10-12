from fastapi import HTTPException

from app.core.crud import READ_LOGIN, build_crud_router
from app.core.enrich import member_count_map
from app.models.family import Family
from app.schemas.common import partial_model
from app.schemas.family import FamilyCreate, FamilyResponse
from app.utils.helpers import clean_text


def check_family_code(db, data: dict, current: Family | None = None) -> None:
    code = data.get("family_code")

    if not code:
        return

    query = db.query(Family).filter(Family.family_code == code)
    if current is not None:
        query = query.filter(Family.id != current.id)

    if query.first():
        raise HTTPException(status_code=400, detail="Family code already exists")


def prepare_family(data: dict) -> dict:
    for key in ("family_code", "head_name", "village", "address", "phone"):
        if isinstance(data.get(key), str):
            data[key] = clean_text(data[key])

    return data


def enrich_families(db, items, user):
    """প্রতিটি পরিবারের সদস্য-সংখ্যা (একটা কুয়েরিতে)"""
    counts = member_count_map(db, [f.id for f in items])

    rows = []
    for family in items:
        data = FamilyResponse.model_validate(family).model_dump(mode="json")
        data["member_count"] = counts.get(family.id, 0)
        rows.append(data)
    return rows


router = build_crud_router(
    prefix="/families",
    tags=["Families"],
    model=Family,
    label="family",
    not_found="Family not found",
    create_schema=FamilyCreate,
    update_schema=partial_model(FamilyCreate, "FamilyUpdate"),
    response_schema=FamilyResponse,
    read_access=READ_LOGIN,
    prepare=prepare_family,
    validate_create=check_family_code,
    validate_update=check_family_code,
    enrich=enrich_families,
    default_limit=50,
    search_fields=[Family.family_code, Family.head_name, Family.village, Family.address, Family.phone],
    filters={"village": (Family.village, "eq")},
)
