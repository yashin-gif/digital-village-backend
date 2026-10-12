from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.announcement import Announcement
from app.models.institution import Institution
from app.models.mosque import Mosque
from app.models.news import News
from app.models.place import Place


router = APIRouter(
    prefix="/public",
    tags=["Public"],
)


@router.get("/summary")
def public_summary(
    db: Session = Depends(get_db),
):
    return {
        "institutions": db.query(Institution).count(),
        "mosques": db.query(Mosque).count(),
        "places": db.query(Place).count(),
        "news": (
            db.query(News)
            .filter(News.is_published.is_(True))
            .count()
        ),
        "announcements": (
            db.query(Announcement)
            .filter(Announcement.is_active.is_(True))
            .count()
        ),
    }