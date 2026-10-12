from sqlalchemy.orm import Session

from app.models.family import Family


def get_family_by_id(
    db: Session,
    family_id: int,
):
    return (
        db.query(Family)
        .filter(Family.id == family_id)
        .first()
    )


def get_all_families(db: Session):
    return (
        db.query(Family)
        .order_by(Family.id.desc())
        .all()
    )