from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.crud import READ_PUBLIC, build_crud_router
from app.core.permissions import is_moderator_or_admin
from app.core.uploads import delete_file, save_image
from app.database import get_db
from app.dependencies import get_current_user
from app.models.mosque import Mosque
from app.models.user import User
from app.schemas.common import partial_model
from app.schemas.mosque import MosqueCreate, MosqueResponse


router = build_crud_router(
    prefix="/mosques",
    tags=["Mosques"],
    model=Mosque,
    label="mosque",
    not_found="Mosque not found",
    create_schema=MosqueCreate,
    update_schema=partial_model(MosqueCreate, "MosqueUpdate"),
    response_schema=MosqueResponse,
    read_access=READ_PUBLIC,
    search_fields=[Mosque.name, Mosque.address, Mosque.imam_name],
)


def _staff_only(user: User) -> None:
    if not is_moderator_or_admin(user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/{mosque_id}/image")
async def upload_mosque_image(
    mosque_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """মসজিদের ছবি বদলানো। পুরনো ছবি মুছে যায়।"""
    _staff_only(current_user)

    item = db.query(Mosque).filter(Mosque.id == mosque_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mosque not found")

    new_url = await save_image(file, "mosques", str(item.id))
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
    return MosqueResponse.model_validate(item).model_dump(mode="json")


@router.delete("/{mosque_id}/image")
def remove_mosque_image(
    mosque_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """মসজিদের ছবি মুছে ফেলা।"""
    _staff_only(current_user)

    item = db.query(Mosque).filter(Mosque.id == mosque_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mosque not found")

    old_url = item.image_url
    item.image_url = None
    db.commit()
    delete_file(old_url)

    db.refresh(item)
    return MosqueResponse.model_validate(item).model_dump(mode="json")