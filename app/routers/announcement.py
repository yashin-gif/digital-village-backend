from app.core.crud import READ_PUBLIC, build_crud_router
from app.core.permissions import is_moderator_or_admin
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse
from app.schemas.common import partial_model


def visible_announcements(db, user):
    """সাধারণ মানুষ শুধু সক্রিয় ঘোষণা দেখবে; মডারেটর/অ্যাডমিন সবই দেখবে।"""
    query = db.query(Announcement)

    if user is None or not is_moderator_or_admin(user.role):
        query = query.filter(Announcement.is_active.is_(True))

    return query


router = build_crud_router(
    prefix="/announcements",
    tags=["Announcements"],
    model=Announcement,
    label="announcement",
    not_found="Announcement not found",
    create_schema=AnnouncementCreate,
    update_schema=partial_model(AnnouncementCreate, "AnnouncementUpdate"),
    response_schema=AnnouncementResponse,
    read_access=READ_PUBLIC,
    search_fields=[Announcement.title],
    list_query=visible_announcements,
)
