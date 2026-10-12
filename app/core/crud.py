"""সাধারণ CRUD রাউটার বানানোর একটাই জায়গা।

প্রতিটি মডিউল (মানুষ, পরিবার, সংবাদ ...) এখান থেকে তার রাউটার বানায়।
কে পড়তে পারবে, কে লিখতে পারবে, কোন তথ্য দেখানো হবে, কতটুকু একসাথে যাবে —
সব এখানে নির্ধারণ করা যায়, তাই নিয়ম সব জায়গায় একই থাকে।

তালিকা API:
  ?q=...          খোঁজ (search_fields এর ভেতরে, অংশ মিললেই হবে)
  ?limit=&offset= পাতা অনুযায়ী (সর্বোচ্চ 200)। উত্তরে X-Total-Count হেডার।
  ?order=asc|desc সাজানো (sort_column অনুযায়ী)
  ?<filter>=...   filters এ ঘোষিত ফিল্টার
"""

from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import forbidden, unauthorized
from app.core.permissions import is_moderator_or_admin
from app.database import get_db
from app.dependencies import get_optional_user, require_staff
from app.models.user import User
from app.services.audit_service import log_action


# কে পড়তে পারবে
READ_PUBLIC = "public"  # সবাই
READ_LOGIN = "login"  # লগইন করা সদস্য
READ_STAFF = "staff"  # শুধু মডারেটর/অ্যাডমিন

MAX_PAGE = 200


def ensure_read(user: User | None, access: str) -> None:
    if access == READ_PUBLIC:
        return

    if user is None:
        raise unauthorized("Login required")

    if access == READ_STAFF and not is_moderator_or_admin(user.role):
        raise forbidden("Moderator or admin permission required")


def check_not_null(model, changes: dict) -> None:
    """আপডেটে যে ফিল্ড খালি হতে পারে না, তাতে null পাঠানো হলে আটকায়।"""
    for name, value in changes.items():
        column = model.__table__.columns.get(name)

        if column is not None and value is None and not column.nullable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{name} cannot be empty",
            )


def get_or_404(db: Session, model, item_id: int, message: str):
    item = db.query(model).filter(model.id == item_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    return item


def escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def convert_value(column, raw: str):
    """URL থেকে আসা লেখাকে কলামের ধরন অনুযায়ী বদলায়।"""
    try:
        python_type = column.type.python_type
    except NotImplementedError:
        python_type = str

    if python_type is bool:
        return raw.lower() in ("1", "true", "yes")
    if python_type is int:
        return int(raw)
    if python_type is date_type:
        return date_type.fromisoformat(raw)
    return raw


def build_crud_router(
    *,
    prefix: str,
    tags: list[str],
    model,
    label: str,
    not_found: str,
    create_schema,
    update_schema,
    response_schema,
    read_access: str = READ_PUBLIC,
    create_guard=require_staff,
    update_guard=require_staff,
    delete_guard=require_staff,
    list_query=None,
    prepare=None,
    validate_create=None,
    validate_update=None,
    serialize=None,
    attach=None,
    enrich=None,
    default_limit: int | None = None,
    search_fields=None,
    filters=None,
    sort_column=None,
) -> APIRouter:
    """
    label          : অডিট লগে নাম (যেমন "person")
    list_query     : (db, user) -> Query, কোন সারি দেখা যাবে তা ঠিক করে
    prepare        : (dict) -> dict, ডেটা পরিষ্কার করে
    validate_create: (db, data, None)   — নতুন তৈরির আগে যাচাই
    validate_update: (db, changes, item) — আপডেটের আগে যাচাই
    serialize      : (obj, user) -> dict, একটা সারির দৃশ্য (ব্যবহারকারী অনুযায়ী)
    enrich         : (db, [obj], user) -> [dict], পুরো পাতা একসাথে — সম্পর্কিত নাম যোগ করে
    attach         : (dict, user) -> dict, তৈরির সময় মালিক (user_id) বসায়
    default_limit  : পাতার আকার না দিলে কতটি যাবে (বড় তালিকায় ব্যবহার)। None = সব
    search_fields  : ?q= এই কলামগুলোতে খোঁজে
    filters        : {"URL নাম": (কলাম, "eq"|"gte"|"lte")}
    sort_column    : ?order= দিয়ে এই কলামে সাজানো হবে (ডিফল্ট: id)
    """
    filters = filters or {}
    response_model = None if (serialize or enrich) else response_schema
    list_response_model = None if (serialize or enrich) else list[response_schema]

    router = APIRouter(prefix=prefix, tags=tags)

    def present_many(db: Session, items, user):
        if enrich:
            return enrich(db, items, user)
        if serialize:
            return [serialize(item, user) for item in items]
        return items

    def base_query(db: Session, user: User | None):
        return list_query(db, user) if list_query else db.query(model)

    def apply_search(query, q: str | None):
        if not q or not search_fields:
            return query

        needle = q.strip()
        if not needle:
            return query

        pattern = f"%{escape_like(needle)}%"
        return query.filter(or_(*[col.ilike(pattern, escape="\\") for col in search_fields]))

    def apply_filters(query, request: Request):
        for name, (column, op) in filters.items():
            raw = request.query_params.get(name)
            if raw is None or raw == "":
                continue

            try:
                value = convert_value(column, raw)
            except (ValueError, TypeError):
                raise HTTPException(status_code=422, detail=f"Invalid value for {name}")

            if op == "gte":
                query = query.filter(column >= value)
            elif op == "lte":
                query = query.filter(column <= value)
            else:
                query = query.filter(column == value)
        return query

    def apply_order(query, order: str):
        column = sort_column if sort_column is not None else model.id
        direction = column.desc() if order == "desc" else column.asc()
        return query.order_by(direction, model.id.desc() if order == "desc" else model.id.asc())

    @router.get("/", response_model=list_response_model)
    def list_items(
        request: Request,
        response: Response,
        q: str | None = Query(None, max_length=100),
        limit: int | None = Query(None, ge=1, le=MAX_PAGE),
        offset: int = Query(0, ge=0),
        order: str = Query("asc", pattern="^(asc|desc)$"),
        db: Session = Depends(get_db),
        user: User | None = Depends(get_optional_user),
    ):
        ensure_read(user, read_access)

        query = apply_search(base_query(db, user), q)
        query = apply_filters(query, request)

        total = query.order_by(None).count()
        response.headers["X-Total-Count"] = str(total)

        query = apply_order(query, order)

        size = limit or default_limit
        if size:
            query = query.offset(offset).limit(size)

        items = query.all()
        return present_many(db, items, user)

    @router.get("/{item_id}", response_model=response_model)
    def get_item(
        item_id: int,
        db: Session = Depends(get_db),
        user: User | None = Depends(get_optional_user),
    ):
        ensure_read(user, read_access)

        item = base_query(db, user).filter(model.id == item_id).first()

        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found)

        return present_many(db, [item], user)[0]

    @router.post("/", response_model=response_model, status_code=status.HTTP_201_CREATED)
    def create_item(
        data: create_schema,
        db: Session = Depends(get_db),
        user: User = Depends(create_guard),
    ):
        payload = data.model_dump()

        if prepare:
            payload = prepare(payload)
        if attach:
            payload = attach(payload, user)
        if validate_create:
            validate_create(db, payload, None)

        item = model(**payload)
        db.add(item)
        db.commit()
        db.refresh(item)

        log_action(db, user.id, f"{label}.create", model.__tablename__, item.id)

        return present_many(db, [item], user)[0]

    @router.patch("/{item_id}", response_model=response_model)
    def update_item(
        item_id: int,
        data: update_schema,
        db: Session = Depends(get_db),
        user: User = Depends(update_guard),
    ):
        item = get_or_404(db, model, item_id, not_found)

        changes = data.model_dump(exclude_unset=True)

        if prepare:
            changes = prepare(changes)
        check_not_null(model, changes)
        if validate_update:
            validate_update(db, changes, item)

        for name, value in changes.items():
            setattr(item, name, value)

        db.commit()
        db.refresh(item)

        log_action(db, user.id, f"{label}.update", model.__tablename__, item.id)

        return present_many(db, [item], user)[0]

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(
        item_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(delete_guard),
    ):
        item = get_or_404(db, model, item_id, not_found)

        db.delete(item)
        db.commit()

        log_action(db, user.id, f"{label}.delete", model.__tablename__, item_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
