from datetime import datetime, timezone
from fastapi import File, UploadFile
from app.core.uploads import delete_avatar, save_avatar
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.core.rate_limit import clear_failures, is_locked, record_failure
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_refresh_token,
    get_reset_token_expiry,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.services.notification_service import send_notification
from app.schemas.auth import (
    DIVISION,
    DISTRICT,
    UPAZILA,
    VILLAGE,
    ForgotPasswordRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    check_birth_year,
)
from app.utils.validators import validate_bd_phone


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def create_user_tokens(user: User) -> dict:
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "tv": user.token_version,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def user_profile(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "birth_year": user.birth_year,
        "email": user.email,
        "phone": user.phone,
        "division": user.division,
        "district": user.district,
        "upazila": user.upazila,
        "village": user.village,
        "para": user.para,
        "photo_url": user.photo_url,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # ইমেইল ঐচ্ছিক: থাকলেই ডুপ্লিকেট চেক হবে
    if user_data.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

    if db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already exists",
        )

    user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        birth_year=user_data.birth_year,
        email=user_data.email or None,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        division=DIVISION,
        district=DISTRICT,
        upazila=UPAZILA,
        village=VILLAGE,
        para=user_data.para,
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return create_user_tokens(user)


# লগইন সীমা
LOGIN_USER_LIMIT = 5     # একই ইউজারনেম/মোবাইলে এতগুলো ভুলের পর বন্ধ
LOGIN_IP_LIMIT = 30      # একই আইপি থেকে এতগুলো ভুলের পর বন্ধ


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = form_data.username.strip()
    ip_key = f"ip:{client_ip(request)}"
    user_key = f"user:{identifier.lower()}"

    # আগে থেকে বন্ধ থাকলে পাসওয়ার্ড যাচাই না করেই ফিরিয়ে দাও
    for key in (user_key, ip_key):
        remaining = is_locked(key)
        if remaining:
            minutes = max(1, remaining // 60)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Try again in about {minutes} minute(s).",
            )

    # লগইন আইডি: ইউজারনেম অথবা মোবাইল নম্বর
    login_phone = None
    try:
        login_phone = validate_bd_phone(identifier)
    except ValueError:
        pass

    user = (
        db.query(User)
        .filter(
            (User.username == identifier)
            | (User.phone == (login_phone or "__none__"))
        )
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        record_failure(user_key, LOGIN_USER_LIMIT)
        record_failure(ip_key, LOGIN_IP_LIMIT)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # সফল লগইনে এই ইউজারের ভুলের হিসাব মুছে যায়
    clear_failures(user_key)

    return create_user_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    payload = decode_refresh_token(token_data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # লগআউট করা টোকেন দিয়ে নতুন টোকেন নেওয়া যাবে না
    if payload.get("tv", 0) != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has ended. Please login again.",
        )

    return create_user_tokens(user)


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email).first()

    # ইমেইল থাকুক বা না থাকুক, উত্তর একই রকম হবে (অ্যাকাউন্ট খোঁজা ঠেকাতে)
    if user:
        reset_token = create_password_reset_token()

        user.reset_token_hash = hash_reset_token(reset_token)
        user.reset_token_expires_at = get_reset_token_expiry()

        db.commit()

        # টোকেন কখনো API উত্তরে ফেরত যাবে না — শুধু ইমেইল/SMS-এ যাবে
        send_notification(
            user.email,
            f"Your password reset token: {reset_token} (valid for 15 minutes)",
        )

    return {
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    token_hash = hash_reset_token(request.token)

    user = (
        db.query(User)
        .filter(User.reset_token_hash == token_hash)
        .first()
    )

    if not user or not user.reset_token_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    expiry = user.reset_token_expires_at

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expiry:
        user.reset_token_hash = None
        user.reset_token_expires_at = None
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    user.password_hash = hash_password(request.new_password)
    user.reset_token_hash = None
    user.reset_token_expires_at = None

    db.commit()

    return {"message": "Password reset successful"}


@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return user_profile(current_user)


class ProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    birth_year: int | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=6, max_length=20)

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return validate_bd_phone(value)
        except ValueError as error:
            raise ValueError(str(error))

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("পুরো নাম কমপক্ষে ২ অক্ষরের হতে হবে")
        return cleaned

    @field_validator("birth_year")
    @classmethod
    def check_birth(cls, value: int | None) -> int | None:
        return check_birth_year(value)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=100)
    new_password: str = Field(min_length=6, max_length=100)


def ensure_unique_for(db: Session, column, value, user_id: int, message: str) -> None:
    taken = db.query(User).filter(column == value, User.id != user_id).first()

    if taken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.patch("/me")
def update_my_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    changes = data.model_dump(exclude_unset=True)

    if "username" in changes and changes["username"] != user.username:
        ensure_unique_for(db, User.username, changes["username"], user.id, "Username already exists")

    if "email" in changes and changes["email"] and changes["email"] != user.email:
        ensure_unique_for(db, User.email, changes["email"], user.id, "Email already exists")

    if "phone" in changes and changes["phone"] != user.phone:
        ensure_unique_for(db, User.phone, changes["phone"], user.id, "Phone number already exists")

    # ইমেইল, নাম ও জন্ম সাল ফাঁকা করা যাবে; ইউজারনেম ও ফোন ফাঁকা করা যাবে না
    for name in ("username", "phone"):
        if name in changes and changes[name] is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{name} cannot be empty")

    for name in ("username", "full_name", "birth_year", "email", "phone"):
        if name in changes:
            setattr(user, name, changes[name] if changes[name] is not None else None)

    db.commit()
    db.refresh(user)

    return user_profile(user)


@router.post("/change-password", response_model=TokenResponse)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if verify_password(data.new_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    user.password_hash = hash_password(data.new_password)
    # অন্য সব ডিভাইসের সেশন বাতিল, এই ডিভাইসে নতুন টোকেন
    user.token_version += 1
    db.commit()
    db.refresh(user)

    return create_user_tokens(user)


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """এই ইউজারের সব টোকেন বাতিল করে (সব ডিভাইসে লগআউট)"""
    user = db.query(User).filter(User.id == current_user.id).first()
    user.token_version += 1
    db.commit()

    return {"message": "Logged out"}


@router.post("/me/photo")
async def upload_my_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """নিজের প্রোফাইল ছবি বদলানো। পুরনো ছবি মুছে যায়।"""
    user = db.query(User).filter(User.id == current_user.id).first()

    new_url = await save_avatar(file, user.id)
    old_url = user.photo_url

    try:
        user.photo_url = new_url
        db.commit()
    except Exception:
        # ডেটাবেস ব্যর্থ হলে নতুন ফাইল মুছে দিই, যাতে ফাইল জমে না থাকে
        delete_avatar(new_url)
        db.rollback()
        raise

    # ডেটাবেস সফল হওয়ার পরেই পুরনো ছবি মোছা হয়
    delete_avatar(old_url)

    return user_profile(user)

@router.delete("/me/photo")
def remove_my_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """নিজের প্রোফাইল ছবি মুছে ফেলা।"""
    user = db.query(User).filter(User.id == current_user.id).first()

    old_url = user.photo_url
    user.photo_url = None
    db.commit()

    delete_avatar(old_url)

    return user_profile(user)