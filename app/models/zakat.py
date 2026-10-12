from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ZakatRecord(Base):
    __tablename__ = "zakat_records"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    record_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )