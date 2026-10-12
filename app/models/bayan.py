from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BayanSession(Base):
    """মসজিদের বয়ানের একটা অধিবেশন"""

    __tablename__ = "bayan_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    mosque_id: Mapped[int | None] = mapped_column(
        ForeignKey("mosques.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    speaker_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    session_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
