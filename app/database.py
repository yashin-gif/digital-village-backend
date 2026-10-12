from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


# বড় ডেটার জন্য (PostgreSQL) কানেকশন পুল: একই সময়ে অনেক ব্যবহারকারী
pool_options = {}
if not settings.database_url.startswith("sqlite"):
    pool_options = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    **pool_options,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()