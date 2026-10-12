from sqlalchemy.orm import Session

from app.models.person import Person


def get_person_by_id(
    db: Session,
    person_id: int,
):
    return (
        db.query(Person)
        .filter(Person.id == person_id)
        .first()
    )


def get_all_people(db: Session):
    return (
        db.query(Person)
        .order_by(Person.id.desc())
        .all()
    )