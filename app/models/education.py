from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    education_level: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    institution_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    subject: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    passing_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    current_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    person = relationship(
        "Person",
        back_populates="educations",
    )