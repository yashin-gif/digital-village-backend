from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    blood_group: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        index=True,
    )

    occupation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    current_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_disabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_widow: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    needs_assistance: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_blood_donor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    family = relationship(
        "Family",
        back_populates="members",
    )
    
    educations = relationship(
    "Education",
    back_populates="person",
    cascade="all, delete-orphan",
   
)