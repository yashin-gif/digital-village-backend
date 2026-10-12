from fastapi import HTTPException

from app.core.crud import READ_STAFF, build_crud_router
from app.core.enrich import person_name_map
from app.dependencies import get_current_user
from app.models.help_request import HelpRequest
from app.models.person import Person
from app.schemas.common import partial_model
from app.schemas.help_request import HelpRequestCreate, HelpRequestResponse


def check_person(db, data: dict, current=None) -> None:
    person_id = data.get("person_id")

    if person_id is not None and not db.query(Person).filter(Person.id == person_id).first():
        raise HTTPException(status_code=404, detail="Person not found")


def attach_owner(payload: dict, user) -> dict:
    return {**payload, "user_id": user.id}


def enrich_help(db, items, user):
    names = person_name_map(db, [h.person_id for h in items])

    rows = []
    for item in items:
        data = HelpRequestResponse.model_validate(item).model_dump(mode="json")
        data["person_name"] = names.get(item.person_id)
        rows.append(data)
    return rows


# আবেদন শুধু মডারেটর/অ্যাডমিন তালিকায় দেখবে; যে কোনো লগইন সদস্য আবেদন করতে পারবে।
# সদস্য নিজের আবেদন দেখে /my/help-requests থেকে।
router = build_crud_router(
    prefix="/help-requests",
    tags=["Help & Welfare"],
    model=HelpRequest,
    label="help_request",
    not_found="Help request not found",
    create_schema=HelpRequestCreate,
    update_schema=partial_model(HelpRequestCreate, "HelpRequestUpdate"),
    response_schema=HelpRequestResponse,
    read_access=READ_STAFF,
    create_guard=get_current_user,
    validate_create=check_person,
    validate_update=check_person,
    attach=attach_owner,
    enrich=enrich_help,
    default_limit=50,
    search_fields=[HelpRequest.title, HelpRequest.request_type],
    filters={
        "status": (HelpRequest.status, "eq"),
        "person_id": (HelpRequest.person_id, "eq"),
        "request_type": (HelpRequest.request_type, "eq"),
    },
)
