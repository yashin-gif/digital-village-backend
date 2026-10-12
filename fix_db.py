"""আধা-তৈরি ডেটাবেস ঠিক করা: যা নেই শুধু সেটুকু যোগ করে, কিছু মোছে না।"""

import os
import shutil
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

DB_FILE = "digital_village.db"

INDEXES = [
    ("ix_people_blood_group", "people", "blood_group"),
    ("ix_people_phone", "people", "phone"),
    ("ix_families_village", "families", "village"),
    ("ix_blood_donors_is_available", "blood_donors", "is_available"),
    ("ix_news_is_published", "news", "is_published"),
    ("ix_announcements_is_active", "announcements", "is_active"),
    ("ix_emergencies_status", "emergencies", "status"),
    ("ix_help_requests_status", "help_requests", "status"),
    ("ix_help_requests_user_id", "help_requests", "user_id"),
]


def columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def index_names(conn):
    return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}


def main():
    if not os.path.exists(DB_FILE):
        print(f"{DB_FILE} পাওয়া যায়নি। প্রজেক্ট ফোল্ডারে আছেন কিনা দেখুন।")
        return

    backup = f"{DB_FILE}.backup-{datetime.now():%Y%m%d-%H%M%S}"
    shutil.copy2(DB_FILE, backup)
    print("ব্যাকআপ:", backup)

    from app.database import Base, engine
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("নতুন টেবিল: যা ছিল না তা তৈরি হয়েছে")

    conn = sqlite3.connect(DB_FILE)

    if "token_version" not in columns(conn, "users"):
        conn.execute("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0")
        print("যোগ হয়েছে: users.token_version")

    if "user_id" not in columns(conn, "help_requests"):
        conn.execute(
            "ALTER TABLE help_requests ADD COLUMN user_id INTEGER "
            "REFERENCES users(id) ON DELETE SET NULL"
        )
        print("যোগ হয়েছে: help_requests.user_id")

    existing = index_names(conn)
    for name, table, column in INDEXES:
        if name not in existing:
            conn.execute(f"CREATE INDEX {name} ON {table} ({column})")
            print("যোগ হয়েছে ইনডেক্স:", name)

    conn.commit()
    conn.close()
    print("ডেটাবেস ঠিক হয়েছে।")


if __name__ == "__main__":
    main()
