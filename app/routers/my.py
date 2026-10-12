from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.help_request import HelpRequest
from app.models.user import User
from app.schemas.help_request import HelpRequestResponse


# লগইন করা সদস্যের নিজের তথ্য। অন্যের আবেদন এখান থেকে দেখা যায় না।
router = APIRouter(
    prefix="/my",
    tags=["My"],
)


@router.get("/help-requests", response_model=list[HelpRequestResponse])
def my_help_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(HelpRequest)
        .filter(HelpRequest.user_id == current_user.id)
        .order_by(HelpRequest.id.desc())
        .all()
    )
