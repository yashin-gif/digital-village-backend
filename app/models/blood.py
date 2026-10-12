from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BloodDonor(Base):
    __tablename__ = "blood_donors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    blood_group: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        index=True,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    last_donation_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    person = relationship("Person")