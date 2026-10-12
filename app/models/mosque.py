from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Mosque(Base):
    __tablename__ = "mosques"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    imam_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    latitude: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    longitude: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # মসজিদের ছবি (ফাইলের পথ)
    image_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )