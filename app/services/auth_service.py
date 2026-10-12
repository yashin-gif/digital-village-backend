from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def make_password(password: str) -> str:
    return hash_password(password)


def check_password(
    password: str,
    password_hash: str,
) -> bool:
    return verify_password(
        password,
        password_hash,
    )


def make_token(user_id: int, username: str, role: str) -> str:
    return create_access_token(
        {
            "sub": str(user_id),
            "username": username,
            "role": role,
        }
    )