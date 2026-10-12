from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.crud import READ_PUBLIC, build_crud_router
from app.core.permissions import is_moderator_or_admin
from app.core.uploads import delete_file, save_image
from app.database import get_db
from app.dependencies import get_current_user
from app.models.news import News
from app.models.user import User
from app.schemas.common import partial_model
from app.schemas.news import NewsCreate, NewsResponse


def visible_news(db, user):
    """সাধারণ মানুষ শুধু প্রকাশিত সংবাদ দেখবে; মডারেটর/অ্যাডমিন খসড়াও দেখবে।"""
    query = db.query(News)

    if user is None or not is_moderator_or_admin(user.role):
        query = query.filter(News.is_published.is_(True))

    return query


router = build_crud_router(
    prefix="/news",
    tags=["News"],
    model=News,
    label="news",
    not_found="News not found",
    create_schema=NewsCreate,
    update_schema=partial_model(NewsCreate, "NewsUpdate"),
    response_schema=NewsResponse,
    read_access=READ_PUBLIC,
    search_fields=[News.title],
    list_query=visible_news,
)


def _staff_only(user: User) -> None:
    if not is_moderator_or_admin(user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/{news_id}/image")
async def upload_news_image(
    news_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """সংবাদের ছবি বদলানো। পুরনো ছবি মুছে যায়।"""
    _staff_only(current_user)

    item = db.query(News).filter(News.id == news_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")

    new_url = await save_image(file, "news", str(item.id))
    old_url = item.image_url

    try:
        item.image_url = new_url
        db.commit()
    except Exception:
        delete_file(new_url)
        db.rollback()
        raise

    delete_file(old_url)
    db.refresh(item)
    return NewsResponse.model_validate(item).model_dump(mode="json")


@router.delete("/{news_id}/image")
def remove_news_image(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """সংবাদের ছবি মুছে ফেলা।"""
    _staff_only(current_user)

    item = db.query(News).filter(News.id == news_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")

    old_url = item.image_url
    item.image_url = None
    db.commit()
    delete_file(old_url)

    db.refresh(item)
    return NewsResponse.model_validate(item).model_dump(mode="json")