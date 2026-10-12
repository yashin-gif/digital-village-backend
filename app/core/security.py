from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


ALGORITHM = "HS256"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

RESET_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: dict,
    expires_minutes: int | None = None,
) -> str:
    payload = data.copy()

    expire_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expire_minutes
    )

    payload.update(
        {
            "type": ACCESS_TOKEN_TYPE,
            "exp": expire,
        }
    )

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def create_refresh_token(data: dict) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload.update(
        {
            "type": REFRESH_TOKEN_TYPE,
            "exp": expire,
        }
    )

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != ACCESS_TOKEN_TYPE:
            return None

        return payload

    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != REFRESH_TOKEN_TYPE:
            return None

        return payload

    except JWTError:
        return None


def create_password_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def get_reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRE_MINUTES
    )