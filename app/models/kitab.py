from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Kitab(Base):
    """পাঠ্য কিতাব"""

    __tablename__ = "kitabs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    author: Mapped[str | None] = mapped_column(String(150), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class KitabProgress(Base):
    """কিতাব পাঠের অগ্রগতি: কোন দিন কতটুকু পড়া হলো"""

    __tablename__ = "kitab_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    kitab_id: Mapped[int] = mapped_column(
        ForeignKey("kitabs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    read_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    from_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    to_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
