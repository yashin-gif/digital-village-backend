from enum import Enum

from app.core.exceptions import forbidden


class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


def is_admin(role: str) -> bool:
    return role == UserRole.ADMIN.value


def is_moderator(role: str) -> bool:
    return role == UserRole.MODERATOR.value


def is_moderator_or_admin(role: str) -> bool:
    return role in {
        UserRole.ADMIN.value,
        UserRole.MODERATOR.value,
    }


def require_admin_role(role: str) -> None:
    if not is_admin(role):
        raise forbidden("Admin permission required")


def require_moderator_or_admin(role: str) -> None:
    if not is_moderator_or_admin(role):
        raise forbidden(
            "Moderator or admin permission required"
        )