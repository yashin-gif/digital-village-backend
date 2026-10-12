from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.crud import escape_like
from app.core.security import hash_password
from app.database import get_db
from app.dependencies import require_admin_user
from app.models.user import User
from app.services.audit_service import log_action
from app.utils.validators import validate_bd_phone


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

ROLE_PATTERN = "^(admin|moderator|user)$"


class AdminUserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr | None = None
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=100)
    role: str = Field(default="user", pattern=ROLE_PATTERN)
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str) -> str:
        try:
            return validate_bd_phone(value)
        except ValueError as error:
            raise ValueError(str(error))


class AdminUserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=6, max_length=20)
    password: str | None = Field(default=None, min_length=6, max_length=100)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return validate_bd_phone(value)
        except ValueError as error:
            raise ValueError(str(error))


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def ensure_unique(db: Session, column, value, exclude_id: int | None, message: str) -> None:
    query = db.query(User).filter(column == value)

    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)

    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.get("/users")
def get_users(
    response: Response,
    q: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    query = db.query(User)

    needle = (q or "").strip()
    if needle:
        pattern = f"%{escape_like(needle)}%"
        query = query.filter(
            or_(
                User.username.ilike(pattern, escape="\\"),
                User.full_name.ilike(pattern, escape="\\"),
                User.email.ilike(pattern, escape="\\"),
                User.phone.ilike(pattern, escape="\\"),
            )
        )

    response.headers["X-Total-Count"] = str(query.count())

    users = query.order_by(User.id).offset(offset).limit(limit).all()

    return [user_to_dict(user) for user in users]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    ensure_unique(db, User.username, data.username, None, "Username already exists")
    ensure_unique(db, User.phone, data.phone, None, "Phone number already exists")
    if data.email:
        ensure_unique(db, User.email, data.email, None, "Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=data.is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(db, current_user.id, "user.create", "users", user.id, f"role={user.role}")

    return user_to_dict(user)


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = get_user_or_404(db, user_id)

    if data.username is not None and data.username != user.username:
        ensure_unique(db, User.username, data.username, user.id, "Username already exists")
        user.username = data.username

    if data.email is not None and data.email != user.email:
        ensure_unique(db, User.email, data.email, user.id, "Email already exists")
        user.email = data.email

    if data.phone is not None and data.phone != user.phone:
        ensure_unique(db, User.phone, data.phone, user.id, "Phone number already exists")
        user.phone = data.phone

    if data.password is not None:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)

    log_action(db, current_user.id, "user.update", "users", user.id)

    return {"message": "User updated successfully", "user": user_to_dict(user)}


@router.patch("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str = Query(..., pattern=ROLE_PATTERN),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = get_user_or_404(db, user_id)

    if user.id == current_user.id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot remove their own admin role",
        )

    old_role = user.role
    user.role = role

    db.commit()
    db.refresh(user)

    log_action(db, current_user.id, "user.role", "users", user.id, f"{old_role}->{role}")

    return {
        "message": "User role updated successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    }


@router.patch("/users/{user_id}/status")
def change_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = get_user_or_404(db, user_id)

    if user.id == current_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot deactivate their own account",
        )

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    log_action(db, current_user.id, "user.status", "users", user.id, f"active={is_active}")

    return {
        "message": "User activated successfully" if is_active else "User deactivated successfully",
        "user_id": user.id,
        "username": user.username,
        "is_active": user.is_active,
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    user = get_user_or_404(db, user_id)

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete their own account",
        )

    username = user.username

    db.delete(user)
    db.commit()

    log_action(db, current_user.id, "user.delete", "users", user_id, f"username={username}")

    return {"message": "User deleted successfully", "user_id": user_id}