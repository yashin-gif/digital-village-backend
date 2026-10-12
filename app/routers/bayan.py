from fastapi import HTTPException

from app.core.crud import READ_PUBLIC, build_crud_router
from app.core.enrich import kitab_title_map, mosque_name_map
from app.core.permissions import is_moderator_or_admin
from app.models.bayan import BayanSession
from app.models.kitab import Kitab, KitabProgress
from app.models.mosque import Mosque
from app.schemas.bayan import BayanCreate, BayanResponse
from app.schemas.common import partial_model
from app.schemas.kitab import KitabCreate, KitabProgressCreate, KitabProgressResponse, KitabResponse


def visible_sessions(db, user):
    """সাধারণ মানুষ শুধু প্রকাশিত বয়ান দেখবে"""
    query = db.query(BayanSession)

    if user is None or not is_moderator_or_admin(user.role):
        query = query.filter(BayanSession.is_published.is_(True))

    return query


def check_mosque_optional(db, data: dict, current=None) -> None:
    mosque_id = data.get("mosque_id")
    if mosque_id is not None and not db.query(Mosque).filter(Mosque.id == mosque_id).first():
        raise HTTPException(status_code=404, detail="Mosque not found")


def enrich_bayan(db, items, user):
    names = mosque_name_map(db, [s.mosque_id for s in items])

    rows = []
    for item in items:
        data = BayanResponse.model_validate(item).model_dump(mode="json")
        data["mosque_name"] = names.get(item.mosque_id)
        rows.append(data)
    return rows


bayan_router = build_crud_router(
    prefix="/bayan",
    tags=["Bayan"],
    model=BayanSession,
    label="bayan",
    not_found="Bayan session not found",
    create_schema=BayanCreate,
    update_schema=partial_model(BayanCreate, "BayanUpdate"),
    response_schema=BayanResponse,
    read_access=READ_PUBLIC,
    list_query=visible_sessions,
    validate_create=check_mosque_optional,
    validate_update=check_mosque_optional,
    enrich=enrich_bayan,
    default_limit=100,
    sort_column=BayanSession.session_date,
    search_fields=[BayanSession.title, BayanSession.speaker_name],
    filters={
        "mosque_id": (BayanSession.mosque_id, "eq"),
        "session_date_from": (BayanSession.session_date, "gte"),
        "session_date_to": (BayanSession.session_date, "lte"),
    },
)

kitab_router = build_crud_router(
    prefix="/kitab",
    tags=["Kitab"],
    model=Kitab,
    label="kitab",
    not_found="Kitab not found",
    create_schema=KitabCreate,
    update_schema=partial_model(KitabCreate, "KitabUpdate"),
    response_schema=KitabResponse,
    read_access=READ_PUBLIC,
    search_fields=[Kitab.title, Kitab.author],
)


def check_kitab_exists(db, data: dict, current=None) -> None:
    kitab_id = data.get("kitab_id")
    if kitab_id is not None and not db.query(Kitab).filter(Kitab.id == kitab_id).first():
        raise HTTPException(status_code=404, detail="Kitab not found")


def enrich_progress(db, items, user):
    titles = kitab_title_map(db, [p.kitab_id for p in items])

    rows = []
    for item in items:
        data = KitabProgressResponse.model_validate(item).model_dump(mode="json")
        data["kitab_title"] = titles.get(item.kitab_id)
        rows.append(data)
    return rows


kitab_progress_router = build_crud_router(
    prefix="/kitab-progress",
    tags=["Kitab"],
    model=KitabProgress,
    label="kitab_progress",
    not_found="Progress record not found",
    create_schema=KitabProgressCreate,
    update_schema=partial_model(KitabProgressCreate, "KitabProgressUpdate"),
    response_schema=KitabProgressResponse,
    read_access=READ_PUBLIC,
    validate_create=check_kitab_exists,
    validate_update=check_kitab_exists,
    enrich=enrich_progress,
    default_limit=100,
    sort_column=KitabProgress.read_date,
    filters={
        "kitab_id": (KitabProgress.kitab_id, "eq"),
        "read_date_from": (KitabProgress.read_date, "gte"),
        "read_date_to": (KitabProgress.read_date, "lte"),
    },
)
