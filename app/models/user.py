from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    # জন্ম সাল (শুধু সাল, যেমন 1985)। সদস্য নিজে দেয় ও বদলায়।
    birth_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ইমেইল ঐচ্ছিক। থাকলে অনন্য থাকবে।
    email: Mapped[str | None] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ঠিকানা: বিভাগ → জেলা → উপজেলা → গ্রাম → পাড়া
    division: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    upazila: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    village: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    para: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # প্রোফাইল ছবির ঠিকানা (ফাইলের পথ)
    photo_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    token_version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    reset_token_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    reset_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )