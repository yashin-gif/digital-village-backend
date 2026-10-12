from fastapi import Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.crud import READ_PUBLIC, build_crud_router
from app.core.permissions import is_moderator_or_admin
from app.core.uploads import delete_file, save_image
from app.database import get_db
from app.dependencies import get_current_user
from app.models.institution import Institution
from app.models.user import User
from app.schemas.common import partial_model
from app.schemas.institution import InstitutionCreate, InstitutionResponse
from app.utils.helpers import clean_text


def prepare_institution(data: dict) -> dict:
    for key in ("name", "institution_type", "address", "phone", "description"):
        if isinstance(data.get(key), str):
            data[key] = clean_text(data[key])

    return data


router = build_crud_router(
    prefix="/institutions",
    tags=["Institutions"],
    model=Institution,
    label="institution",
    not_found="Institution not found",
    create_schema=InstitutionCreate,
    update_schema=partial_model(InstitutionCreate, "InstitutionUpdate"),
    response_schema=InstitutionResponse,
    read_access=READ_PUBLIC,
    search_fields=[Institution.name, Institution.institution_type, Institution.address],
    prepare=prepare_institution,
)


def _staff_only(user: User) -> None:
    if not is_moderator_or_admin(user.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/{institution_id}/image")
async def upload_institution_image(
    institution_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """প্রতিষ্ঠানের ছবি বদলানো। পুরনো ছবি মুছে যায়।"""
    _staff_only(current_user)

    item = db.query(Institution).filter(Institution.id == institution_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    new_url = await save_image(file, "institutions", str(item.id))
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
    return InstitutionResponse.model_validate(item).model_dump(mode="json")


@router.delete("/{institution_id}/image")
def remove_institution_image(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """প্রতিষ্ঠানের ছবি মুছে ফেলা।"""
    _staff_only(current_user)

    item = db.query(Institution).filter(Institution.id == institution_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

    old_url = item.image_url
    item.image_url = None
    db.commit()
    delete_file(old_url)

    db.refresh(item)
    return InstitutionResponse.model_validate(item).model_dump(mode="json")