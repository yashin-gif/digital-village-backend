from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import validate_bd_phone


# ঠিকানার তালিকা (বগারচর, বকশীগঞ্জ, জামালপুর, ময়মনসিংহ)
DIVISION = "ময়মনসিংহ"
DISTRICT = "জামালপুর"
UPAZILA = "বকশীগঞ্জ"
VILLAGE = "বগারচর"

PARAS = {
    "উত্তর পাড়া",
    "দক্ষিণ পাড়া",
    "নামা পাড়া",
    "আলুর চর",
    "বান্দের পাড়",
    "ঘেগা পাড়া",
    "ইছাপুরা",
    "কলনি",
    "মধ্য পাড়া",
}

MIN_BIRTH_YEAR = 1900


def max_birth_year() -> int:
    return date.today().year


def check_birth_year(value: int | None) -> int | None:
    if value is None:
        return None
    if not (MIN_BIRTH_YEAR <= value <= max_birth_year()):
        raise ValueError(
            f"জন্ম সাল {MIN_BIRTH_YEAR} থেকে {max_birth_year()} এর মধ্যে হতে হবে"
        )
    return value


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=100)
    para: str = Field(min_length=2, max_length=50)
    birth_year: int | None = None

    @field_validator("phone")
    @classmethod
    def check_phone(cls, value: str) -> str:
        try:
            return validate_bd_phone(value)
        except ValueError as error:
            raise ValueError(str(error))

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("পুরো নাম কমপক্ষে ২ অক্ষরের হতে হবে")
        return cleaned

    @field_validator("para")
    @classmethod
    def check_para(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if cleaned not in PARAS:
            raise ValueError("সঠিক পাড়া বাছাই করুন")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("birth_year")
    @classmethod
    def check_birth(cls, value: int | None) -> int | None:
        return check_birth_year(value)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"