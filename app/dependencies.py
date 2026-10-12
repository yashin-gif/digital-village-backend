from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import unauthorized
from app.core.permissions import require_admin_role, require_moderator_or_admin
from app.core.security import decode_access_token
from app.database import SessionLocal
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

# টোকেন না থাকলেও চলবে (সর্বজনীন পেজ, কিন্তু অ্যাডমিন/মডারেটর হলে বেশি তথ্য দেখাবে)
oauth2_optional_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)

    if not payload:
        raise unauthorized("Invalid or expired token")

    user_id = payload.get("sub")

    if not user_id:
        raise unauthorized("Invalid token")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise unauthorized("Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise unauthorized("User not found")

    if not user.is_active:
        raise unauthorized("User account is inactive")

    # লগআউট বা পাসওয়ার্ড বদলের পর আগের টোকেন অচল
    if payload.get("tv", 0) != user.token_version:
        raise unauthorized("Session has ended. Please login again.")

    return user


def get_optional_user(
    token: str | None = Depends(oauth2_optional_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None

    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """মডারেটর বা অ্যাডমিন"""
    require_moderator_or_admin(current_user.role)
    return current_user


def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """শুধু অ্যাডমিন"""
    require_admin_role(current_user.role)
    return current_user
