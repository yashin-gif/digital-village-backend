from sqlalchemy.orm import Session

from app.models.help_request import HelpRequest


def get_pending_help_requests(db: Session):
    return (
        db.query(HelpRequest)
        .filter(HelpRequest.status == "pending")
        .order_by(HelpRequest.id.desc())
        .all()
    )