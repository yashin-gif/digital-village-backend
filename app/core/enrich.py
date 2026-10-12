"""তালিকায় সম্পর্কিত নাম যোগ করার সহায়ক।

প্রতিটি সারির জন্য আলাদা কুয়েরি না করে, পুরো পাতার আইডিগুলো একবারে খুঁজে আনা হয়।
লক্ষাধিক রেকর্ডেও এতে কুয়েরির সংখ্যা স্থির থাকে।
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.family import Family
from app.models.kitab import Kitab
from app.models.mosque import Mosque
from app.models.person import Person


def full_name(person: Person) -> str:
    return " ".join(part for part in [person.first_name, person.last_name] if part)


def person_map(db: Session, ids) -> dict:
    ids = {i for i in ids if i is not None}
    if not ids:
        return {}
    return {p.id: p for p in db.query(Person).filter(Person.id.in_(ids)).all()}


def person_name_map(db: Session, ids) -> dict:
    return {pid: full_name(p) for pid, p in person_map(db, ids).items()}


def family_head_map(db: Session, ids) -> dict:
    ids = {i for i in ids if i is not None}
    if not ids:
        return {}
    return dict(db.query(Family.id, Family.head_name).filter(Family.id.in_(ids)).all())


def member_count_map(db: Session, family_ids) -> dict:
    ids = {i for i in family_ids if i is not None}
    if not ids:
        return {}
    rows = (
        db.query(Person.family_id, func.count(Person.id))
        .filter(Person.family_id.in_(ids))
        .group_by(Person.family_id)
        .all()
    )
    return {family_id: count for family_id, count in rows}


def mosque_name_map(db: Session, ids) -> dict:
    ids = {i for i in ids if i is not None}
    if not ids:
        return {}
    return dict(db.query(Mosque.id, Mosque.name).filter(Mosque.id.in_(ids)).all())


def kitab_title_map(db: Session, ids) -> dict:
    ids = {i for i in ids if i is not None}
    if not ids:
        return {}
    return dict(db.query(Kitab.id, Kitab.title).filter(Kitab.id.in_(ids)).all())
